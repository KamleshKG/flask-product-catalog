from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from app.extensions import init_extensions
from app.utils.logging import configure_logging


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    # Configure logging
    configure_logging(app)

    # Initialize extensions
    init_extensions(app)

    # Configure tracing if enabled
    if app.config['ENABLE_TRACING']:
        trace.set_tracer_provider(TracerProvider())
        jaeger_exporter = JaegerExporter(
            agent_host_name=app.config['JAEGER_HOST'],
            agent_port=app.config['JAEGER_PORT'],
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )

    # Register blueprints
    from app.routes.products import products_bp
    from app.routes.auth import auth_bp
    app.register_blueprint(products_bp)
    app.register_blueprint(auth_bp)

    # Add middleware
    from app.middleware import log_request
    app.before_request(log_request)

    return app