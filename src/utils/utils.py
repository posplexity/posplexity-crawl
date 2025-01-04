import asyncio

async def async_wrapper(tasks: list) -> list:
    """
    여러 비동기 작업을 비동기 함수 내에서 실행하는 함수입니다.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 이미 실행 중인 이벤트 루프가 있는 경우
        return await asyncio.gather(*tasks)
    else:
        # 새로운 이벤트 루프를 생성하는 경우
        return asyncio.run(asyncio.gather(*tasks))