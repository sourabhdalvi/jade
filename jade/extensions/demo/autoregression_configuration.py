"""
Implement JobConfiguration for auto-regression analysis.
"""
from jade.jobs.job_container_by_key import JobContainerByKey
from jade.jobs.job_configuration import JobConfiguration
from jade.extensions.demo.autoregression_parameters import AutoRegressionParameters
from jade.extensions.demo.autoregression_execution import AutoRegressionExecution


class AutoRegressionConfiguration(JobConfiguration):
    """
    A class used to configure auto-regression jobs
    """

    def __init__(self, job_inputs, job_execution_class, **kwargs):
        """
        Init AutoRegression class

        Parameters
        ----------
        job_inputs: :obj:`AutoRegressionInputs`
            The instance of :obj:`AutoRegressionInputs`
        job_execution_class: :obj:`AutoRegressionExecution`
            Class :class:`AutoRegressionExecution`
        kwargs, extra arguments
        """

        if isinstance(job_execution_class, str) and "AutoRegressionExecution" in job_execution_class:
            job_execution_class = AutoRegressionExecution

        super(AutoRegressionConfiguration, self).__init__(
            inputs=job_inputs,
            container=JobContainerByKey(),
            job_parameters_class=AutoRegressionParameters,
            job_execution_class=job_execution_class,
            **kwargs
        )

    def _serialize(self, data):
        """Fill in instance-specific information."""
        pass

    def _transform_for_local_execution(self, scratch_dir, are_inputs_local):
        """Transform data for efficient execution"""
        pass

    def create_from_result(self, job, output_dir):
        """Create instance from result"""
        return None

    def get_job_inputs(self):
        """Get the instance of :obj:`JobInputs`"""
        return self._inputs
