from app.bot import app
from app.bot.monitor import monitor
import asyncio


async def main():
    # Start the RSI monitor in the background
    monitor_task = asyncio.create_task(monitor.start_monitoring())
    
    # Start the Telegram bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        # Keep running
        await monitor_task
    except KeyboardInterrupt:
        print("Shutting down...")
        await monitor.stop_monitoring()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
