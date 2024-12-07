import sentry_sdk

from utils.settings import settings


def init_sentry():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        # traces_sample_rate=1.0,
    )


if __name__ == '__main__':
    init_sentry()
    print(1 / 0)
