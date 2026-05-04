
from sqlalchemy.orm import Session
from app.modules.users.models import User
from . import schemas
from app.core.logging import get_recent_activity_log

def get_dashboard_cliente(db: Session, user: User) -> schemas.ClientDashboardOut:
    # Información de la empresa asociada al usuario
    company_info = {}
    if user.company:
        company_info = {
            "id": user.company.id,
            "name": user.company.name,
            "rfc": user.company.rfc,
            "address": user.company.address,
            "phone": user.company.phone,
            "email": user.company.email,
            "active": user.company.active,
            "observations": user.company.observations
        }
    # Órdenes del cliente
    orders = db.query(user.__class__).filter_by(id=user.id).first().orders_client
    total_orders = len(orders)
    # Conteo por estado
    orders_by_status = {}
    for order in orders:
        status = order.status.name if order.status else "Desconocido"
        orders_by_status[status] = orders_by_status.get(status, 0) + 1
    # Total pagado
    total_paid = float(sum(float(order.total_payment or 0) for order in orders if order.status and order.status.name.lower() == "completada"))
    # Carrito
    cart = user.cart
    cart_products_count = sum(cd.quantity for cd in cart.cart_details) if cart and cart.cart_details else 0
    # Pagos por estado
    payment_status = schemas.PaymentStatusSummary()
    for order in orders:
        for payment in order.payments:
            status = payment.status.name.lower() if payment.status else ""
            if status == "pendiente":
                payment_status.pending += 1
            elif status == "pagado":
                payment_status.paid += 1
            elif status == "rechazado":
                payment_status.rejected += 1
            elif status == "cancelado":
                payment_status.cancelled += 1
    # Incidencias: órdenes con estado "incidencia" o similar
    incidents = [
        {
            "order_id": order.id,
            "folio": order.folio,
            "status": order.status.name if order.status else None,
            "total_payment": float(order.total_payment or 0)
        }
        for order in orders if order.status and "incidencia" in order.status.name.lower()
    ]
    # Gráfica de pastel: estado de las órdenes
    pie_labels = list(orders_by_status.keys())
    pie_values = list(orders_by_status.values())
    orders_pie = schemas.PieChartData(labels=pie_labels, values=pie_values)
    # Gráfica de barras: compras por mes
    from collections import Counter
    bar_counter = Counter()
    for order in orders:
        if hasattr(order, "created_at") and order.created_at:
            month = order.created_at.strftime("%Y-%m")
            bar_counter[month] += 1
    bar_labels = sorted(bar_counter.keys())
    bar_values = [bar_counter[m] for m in bar_labels]
    orders_bar = schemas.BarChartData(labels=bar_labels, values=bar_values)
    recent_activity = get_recent_activity_log(10)
    return schemas.ClientDashboardOut(
        total_orders=total_orders,
        orders_by_status=orders_by_status,
        total_paid=total_paid,
        cart_products_count=cart_products_count,
        payment_status=payment_status,
        incidents=incidents,
        orders_pie=orders_pie,
        orders_bar=orders_bar,
        recent_activity=recent_activity,
        company_info=company_info
    )

def get_dashboard_asesor(db: Session, user: User) -> schemas.AdvisorDashboardOut:
    # Órdenes gestionadas por el asesor
    orders = db.query(user.__class__).filter_by(id=user.id).first().orders_advisor
    # Gráfica de empresas: cantidad de órdenes gestionadas por empresa
    from app.modules.companies.models import Company
    company_counter = {}
    for order in orders:
        if order.company:
            name = order.company.name
            company_counter[name] = company_counter.get(name, 0) + 1
    companies_pie = schemas.PieChartData(labels=list(company_counter.keys()), values=list(company_counter.values()))
    total_orders = len(orders)
    # Clientes únicos asignados
    client_ids = set(order.client_id for order in orders if order.client_id)
    total_clients = len(client_ids)
    # Conteo por estado
    orders_by_status = {}
    for order in orders:
        status = order.status.name if order.status else "Desconocido"
        orders_by_status[status] = orders_by_status.get(status, 0) + 1
    # Productos gestionados (únicos en órdenes gestionadas)
    product_ids = set()
    for order in orders:
        for detail in order.order_details:
            product_ids.add(detail.product_id)
    products_managed = len(product_ids)
    # Pagos por estado
    payment_status = schemas.PaymentStatusSummary()
    for order in orders:
        for payment in order.payments:
            status = payment.status.name.lower() if payment.status else ""
            if status == "pendiente":
                payment_status.pending += 1
            elif status == "pagado":
                payment_status.paid += 1
            elif status == "rechazado":
                payment_status.rejected += 1
            elif status == "cancelado":
                payment_status.cancelled += 1
    # Incidencias: órdenes con estado "incidencia" o similar
    incidents = [
        {
            "order_id": order.id,
            "folio": order.folio,
            "status": order.status.name if order.status else None,
            "total_payment": float(order.total_payment or 0)
        }
        for order in orders if order.status and "incidencia" in order.status.name.lower()
    ]
    # Gráfica de pastel: estado de las órdenes
    pie_labels = list(orders_by_status.keys())
    pie_values = list(orders_by_status.values())
    orders_pie = schemas.PieChartData(labels=pie_labels, values=pie_values)
    # Gráfica de barras: órdenes gestionadas por mes
    from collections import Counter
    bar_counter = Counter()
    for order in orders:
        if hasattr(order, "created_at") and order.created_at:
            month = order.created_at.strftime("%Y-%m")
            bar_counter[month] += 1
    bar_labels = sorted(bar_counter.keys())
    bar_values = [bar_counter[m] for m in bar_labels]
    orders_bar = schemas.BarChartData(labels=bar_labels, values=bar_values)
    recent_activity = get_recent_activity_log(10)
    return schemas.AdvisorDashboardOut(
        total_clients=total_clients,
        total_orders=total_orders,
        orders_by_status=orders_by_status,
        products_managed=products_managed,
        payment_status=payment_status,
        incidents=incidents,
        orders_pie=orders_pie,
        orders_bar=orders_bar,
        recent_activity=recent_activity,
        companies_pie=companies_pie
    )

def get_dashboard_admin(db: Session) -> schemas.AdminDashboardOut:
    # Usuarios y roles
    users = db.query(User).all()
    total_users = len(users)
    role_counter = {}
    for u in users:
        role = u.role.name.lower() if u.role else "otro"
        role_counter[role] = role_counter.get(role, 0) + 1
    total_clients = role_counter.get("cliente", 0)
    total_advisors = role_counter.get("asesor", 0)
    total_admins = role_counter.get("administrador", 0) + role_counter.get("admin", 0)
    # Empresas
    from app.modules.companies.models import Company
    companies = db.query(Company).all()
    total_companies = len(companies)
    # Órdenes
    from app.modules.orders.models import Order
    orders = db.query(Order).all()
    total_orders = len(orders)
    # Pagos
    from app.modules.payments.models import Payment
    payments = db.query(Payment).all()
    total_payments = float(sum(float(p.amount or 0) for p in payments if p.status and p.status.name.lower() == "autorizado"))
    # Productos
    from app.modules.products.models import Product
    products = db.query(Product).all()
    total_products = len(products)
    active_products = len([p for p in products if p.active])
    inactive_products = total_products - active_products
    # Productos en carritos
    from app.modules.carts.models import CartDetail
    products_in_carts = db.query(CartDetail).count()
    # Pagos por estado
    payment_status = schemas.PaymentStatusSummary()
    for p in payments:
        status = p.status.name.lower() if p.status else ""
        if status == "pendiente":
            payment_status.pending += 1
        elif status == "pagado":
            payment_status.paid += 1
        elif status == "rechazado":
            payment_status.rejected += 1
        elif status == "cancelado":
            payment_status.cancelled += 1
    # Órdenes por estado
    orders_by_status = {}
    for order in orders:
        status = order.status.name if order.status else "Desconocido"
        orders_by_status[status] = orders_by_status.get(status, 0) + 1
    # Incidencias: órdenes con estado "incidencia" o similar
    incidents = [
        {
            "order_id": order.id,
            "folio": order.folio,
            "status": order.status.name if order.status else None,
            "total_payment": float(order.total_payment or 0)
        }
        for order in orders if order.status and "incidencia" in order.status.name.lower()
    ]
    # Gráfica de pastel: distribución de roles
    user_roles_pie = schemas.PieChartData(labels=list(role_counter.keys()), values=list(role_counter.values()))
    # Gráfica de pastel: estado global de las órdenes
    orders_pie = schemas.PieChartData(labels=list(orders_by_status.keys()), values=list(orders_by_status.values()))
    # Gráfica de pastel: productos activos vs inactivos
    products_pie = schemas.PieChartData(labels=["Activos", "Inactivos"], values=[active_products, inactive_products])
    # Gráfica de barras: órdenes por mes
    from collections import Counter
    bar_counter = Counter()
    for order in orders:
        if hasattr(order, "created_at") and order.created_at:
            month = order.created_at.strftime("%Y-%m")
            bar_counter[month] += 1
    bar_labels = sorted(bar_counter.keys())
    bar_values = [bar_counter[m] for m in bar_labels]
    orders_bar = schemas.BarChartData(labels=bar_labels, values=bar_values)
    # Gráfica de barras: pagos por mes
    pay_counter = Counter()
    for p in payments:
        if hasattr(p, "created_at") and p.created_at:
            month = p.created_at.strftime("%Y-%m")
            pay_counter[month] += 1
    pay_labels = sorted(pay_counter.keys())
    pay_values = [pay_counter[m] for m in pay_labels]
    payments_bar = schemas.BarChartData(labels=pay_labels, values=pay_values)
    recent_activity = get_recent_activity_log(10)
    return schemas.AdminDashboardOut(
        total_users=total_users,
        total_clients=total_clients,
        total_advisors=total_advisors,
        total_admins=total_admins,
        total_companies=total_companies,
        total_orders=total_orders,
        total_payments=total_payments,
        total_products=total_products,
        active_products=active_products,
        inactive_products=inactive_products,
        products_in_carts=products_in_carts,
        payment_status=payment_status,
        orders_by_status=orders_by_status,
        user_roles_pie=user_roles_pie,
        orders_pie=orders_pie,
        products_pie=products_pie,
        orders_bar=orders_bar,
        payments_bar=payments_bar,
        incidents=incidents,
        recent_activity=recent_activity
    )
