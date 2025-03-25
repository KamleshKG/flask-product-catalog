from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.utils.metrics import PRODUCT_VIEWS, PRODUCT_UPDATES
from app.utils.governance import permission_required, audit_log
from app.services.product_service import ProductService
import time

products_bp = Blueprint('products', __name__)


@products_bp.route('/products', methods=['GET'])
@login_required
@permission_required('product:read')
def get_products():
    products = ProductService.get_all_products()

    # Record metrics
    for product in products:
        PRODUCT_VIEWS.labels(product_id=product.id).inc()

    # Audit log
    audit_log(
        user_id=current_user.id,
        action='view_products',
        details={'count': len(products)}
    )

    return jsonify([p.to_dict() for p in products])


@products_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
@permission_required('product:update')
@limiter.limit("10 per minute")
def update_product(id):
    data = request.get_json()
    product = ProductService.update_product(id, data)

    if product:
        PRODUCT_UPDATES.inc()
        audit_log(
            user_id=current_user.id,
            action='update_product',
            details={'product_id': id, 'changes': data}
        )
        return jsonify(product.to_dict())
    return jsonify({"error": "Product not found"}), 404


@products_bp.route('/products', methods=['POST'])
@login_required
@permission_required('product:create')
def create_product():
    data = request.get_json()
    product = ProductService.create_product(data)

    audit_log(
        user_id=current_user.id,
        action='create_product',
        details={'product': product.to_dict()}
    )
    return jsonify(product.to_dict()), 201


@products_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
@permission_required('product:delete')
def delete_product(id):
    success = ProductService.delete_product(id)

    if success:
        audit_log(
            user_id=current_user.id,
            action='delete_product',
            details={'product_id': id}
        )
        return jsonify({"message": "Product deleted"})
    return jsonify({"error": "Product not found"}), 404