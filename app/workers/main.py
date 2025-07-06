import redis
from rq import Worker, Queue, Connection
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis connection
redis_conn = redis.from_url(settings.REDIS_URL)

# Define queues
deal_queue = Queue('deals', connection=redis_conn)
pricing_queue = Queue('pricing', connection=redis_conn)
general_queue = Queue('general', connection=redis_conn)

def main():
    """Main worker process"""
    logger.info("Starting RQ worker...")
    
    with Connection(redis_conn):
        worker = Worker([deal_queue, pricing_queue, general_queue])
        worker.work()

if __name__ == '__main__':
    main()
