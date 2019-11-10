"""Tests HpcManager functionality."""

import copy
import os

import pytest

from jade.common import OUTPUT_DIR
from jade.hpc.common import HpcType
from jade.hpc.hpc_manager import HpcManager
from jade.hpc.slurm_manager import SlurmManager
from jade.jobs.job_submitter import DEFAULTS
from jade.exceptions import InvalidParameter
from jade.utils.utils import dump_data, load_data


HPC_CONFIG = load_data(DEFAULTS["hpc_config_file"])


def hpc_config():
    return copy.deepcopy(HPC_CONFIG)


class TestHpc(object):

    def test_create_slurm(self):
        self.create_hpc_manager("eagle", hpc_config())

        bad_config = hpc_config()
        bad_config["hpc"].pop("allocation")
        with pytest.raises(InvalidParameter):
            self.create_hpc_manager("eagle", bad_config)

        optional_config = copy.deepcopy(hpc_config())
        optional_config["hpc"].pop("mem")
        mgr = self.create_hpc_manager("eagle", optional_config)
        assert "mem" in mgr.get_hpc_config()["hpc"]

    def test_create_slurm_invalid_file(self):
        original = os.environ.get("NREL_CLUSTER")
        os.environ["NREL_CLUSTER"] = "eagle"
        with pytest.raises(FileNotFoundError):
            HpcManager("invalid_filename", OUTPUT_DIR)

        if original is None:
            os.environ.pop("NREL_CLUSTER")
        else:
            os.environ["NREL_CLUSTER"] = original

    def test_create_pbs(self):
        self.create_hpc_manager("peregrine", hpc_config())

    def test_create_submission_script(self):
        config = hpc_config()
        mgr = self.create_hpc_manager("eagle", config)
        script = "run.sh"
        required = ["account", "time", "job-name", "output",
                    "error", "#SBATCH"]
        required += [script]
        try:
            submission_script = "submit.sh"
            mgr._intf.create_submission_script("test", script,
                                               submission_script, ".")
            assert os.path.exists(submission_script)
            with open(submission_script) as fp_in:
                data = fp_in.read()
                for term in required:
                    assert term in data
        finally:
            os.remove(submission_script)

    def test_qos_setting(self):
        config = hpc_config()

        # With qos set.
        config["hpc"]["qos"] = "high"
        mgr = self.create_hpc_manager("eagle", config)
        text = mgr._intf._create_submission_script_text("name", "run.sh", ".")
        found = False
        for line in text:
            if "qos" in line:
                found = True
        assert found

        # With qos not set.
        config = hpc_config()
        if "hpc" in config["hpc"]:
            config["hpc"].pop("qos")
        mgr = self.create_hpc_manager("eagle", config)
        text = mgr._intf._create_submission_script_text("name", "run.sh", ".")
        found = False
        for line in text:
            if "qos" in line:
                found = True
        assert not found

    def test_get_stripe_count(self):
        output = "stripe_count:  16 stripe_size:   1048576 stripe_offset: -1"
        assert SlurmManager._get_stripe_count(output) == 16

    @staticmethod
    def create_hpc_manager(cluster, config):
        original = os.environ.get("NREL_CLUSTER")
        os.environ["NREL_CLUSTER"] = cluster
        mgr = None
        try:
            hpc_file = "test-hpc-config.toml"
            dump_data(config, hpc_file)

            mgr = HpcManager(hpc_file, OUTPUT_DIR)
        finally:
            os.remove(hpc_file)

        if cluster == "eagle":
            assert mgr.hpc_type == HpcType.SLURM
        elif cluster == "peregrine":
            assert mgr.hpc_type == HpcType.PBS
        else:
            assert False, "unknown cluster={}".format(cluster)

        if original is None:
            os.environ.pop("NREL_CLUSTER")
        else:
            os.environ["NREL_CLUSTER"] = original

        return mgr
