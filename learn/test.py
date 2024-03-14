from greenlet import greenlet
import time
import asyncio

    # def func1():
    #     print(1)
    #     gr2.switch()
    #     print(3)
    #     gr2.switch()
    # def func2():
    #     print(2)
async def func():
    print(1)
    await asyncio.sleep(2)
    print(2)
    return 'xxx'
async def main():
    print('main start')
    task_list=[asyncio.create_task(func(),name='a'),
               asyncio.create_task(func(),name='b')]
    done=await asyncio.wait(task_list,timeout=None)
    print(done)
asyncio.run(main())
