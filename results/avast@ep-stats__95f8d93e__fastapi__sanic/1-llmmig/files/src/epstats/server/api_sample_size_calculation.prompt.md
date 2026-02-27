The following Python code currently uses the library "fastapi" version 0.111.1.
Migrate this code to use the library "sanic" version 25.3.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "fastapi" to "sanic".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "fastapi" and "sanic".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException

from ..toolkit.statistics import Statistics
from .req import SampleSizeCalculationData
from .res import SampleSizeCalculationResult

_logger = logging.getLogger("epstats")


def get_sample_size_calculation_router(get_executor_pool) -> APIRouter:
    def _sample_size_calculation(data: SampleSizeCalculationData):
        try:
            if data.std is None:
                f = Statistics.required_sample_size_per_variant_bernoulli
            else:
                f = Statistics.required_sample_size_per_variant

            sample_size_per_variant = f(**data.dict())

            _logger.info((f"Calculation finished, sample_size_per_variant = {sample_size_per_variant}."))
            return SampleSizeCalculationResult(sample_size_per_variant=sample_size_per_variant)
        except Exception as e:
            _logger.error(f"Cannot calculate the sample size because of: '{e}'")
            _logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail=f"Cannot calculate the sample size because of: '{e}'",
            )

    router = APIRouter()

    @router.post("/sample-size-calculation", response_model=SampleSizeCalculationResult)
    async def sample_size_calculation(
        data: SampleSizeCalculationData,
        evaluation_pool: ThreadPoolExecutor = Depends(get_executor_pool),
    ):
        """
        Calculates sample size based on `data`.
        """
        _logger.info(f"Calling the sample size calculation with {data.json()}")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(evaluation_pool, _sample_size_calculation, data)

    return router

```