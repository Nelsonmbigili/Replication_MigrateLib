### Explanation of Changes
To migrate the code from `fastapi` to `sanic`, the following changes were made:
1. **Sanic Imports**: Replaced `fastapi` imports with `sanic` equivalents. Specifically:
   - Replaced `APIRouter` with `Sanic` (the main app object in Sanic).
   - Removed `Depends` and replaced dependency injection with direct function calls.
   - Replaced `HTTPException` with `SanicException` for error handling.
2. **Request and Response Handling**:
   - Replaced `@router.post` with `@app.post` since Sanic uses the app object to define routes.
   - Used `request.json` to access the request body instead of relying on `data` being automatically parsed.
   - Used `json` to return responses instead of `response_model`.
3. **Concurrency**:
   - Sanic uses `loop.run_in_executor` for running blocking code in a thread pool, similar to FastAPI. This remains unchanged.
4. **Logging**:
   - Logging remains the same since it is independent of the framework.
5. **Sanic App Creation**:
   - Created a `Sanic` app object and added the route directly to it.

### Modified Code
Here is the complete code after migrating to `sanic`:

```python
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from sanic import Sanic, response
from sanic.exceptions import SanicException

from ..toolkit.statistics import Statistics
from .req import SampleSizeCalculationData
from .res import SampleSizeCalculationResult

_logger = logging.getLogger("epstats")


def get_sample_size_calculation_app(get_executor_pool) -> Sanic:
    app = Sanic("SampleSizeCalculationApp")

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
            raise SanicException(
                f"Cannot calculate the sample size because of: '{e}'", status_code=500
            )

    @app.post("/sample-size-calculation")
    async def sample_size_calculation(request):
        """
        Calculates sample size based on `data`.
        """
        try:
            data = SampleSizeCalculationData(**request.json)
        except Exception as e:
            _logger.error(f"Invalid request data: {e}")
            raise SanicException(f"Invalid request data: {e}", status_code=400)

        _logger.info(f"Calling the sample size calculation with {data.json()}")
        evaluation_pool = get_executor_pool()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(evaluation_pool, _sample_size_calculation, data)
        return response.json(result.dict())

    return app
```

### Key Points in the Modified Code
1. **Sanic App**: The `Sanic` app object is created using `Sanic("SampleSizeCalculationApp")`.
2. **Route Definition**: The route is defined using `@app.post` instead of `@router.post`.
3. **Request Parsing**: The request body is accessed using `request.json`, and the `SampleSizeCalculationData` object is instantiated manually.
4. **Error Handling**: `SanicException` is used for raising HTTP errors.
5. **Response**: The response is returned using `response.json`, and the result is converted to a dictionary using `result.dict()`.

This code is now fully migrated to use `sanic` version 25.3.0.