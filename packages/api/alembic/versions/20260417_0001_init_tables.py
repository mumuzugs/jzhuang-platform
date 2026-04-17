"""init tables

Revision ID: 20260417_0001
Revises: 
Create Date: 2026-04-17 18:05:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260417_0001"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = sa.Enum("FREE", "PRO", "ADMIN", name="userrole")
user_status_enum = sa.Enum("ACTIVE", "DISABLED", "DELETED", name="userstatus")
design_style_enum = sa.Enum("MODERN_SIMPLE", "NORDIC", "CHINESE", name="designstyle")
layout_type_enum = sa.Enum("SPACE_UTILIZATION", "FAMILY_FRIENDLY", "SIMPLE_OPEN", name="layouttype")
design_status_enum = sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="designstatus")
inspection_status_enum = sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="inspectionstatus")
inspection_risk_level_enum = sa.Enum("LOW", "MEDIUM", "HIGH", name="inspectionrisklevel")
construction_status_enum = sa.Enum("NOT_STARTED", "IN_PROGRESS", "COMPLETED", "SUSPENDED", name="constructionstatus")
node_status_enum = sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "OVERDUE", name="nodestatus")
order_status_enum = sa.Enum("PENDING", "PAID", "CANCELLED", "REFUNDED", name="orderstatus")
payment_method_enum = sa.Enum("WECHAT", "ALIPAY", name="paymentmethod")


def upgrade() -> None:
    # Enums created implicitly by SQLAlchemy during CREATE TABLE
    # Do NOT call create() here to avoid DuplicateObjectError

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("phone", sa.String(length=11), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("nickname", sa.String(length=50), nullable=True),
        sa.Column("avatar", sa.String(length=500), nullable=True),
        sa.Column("role", user_role_enum, nullable=False, server_default="FREE"),
        sa.Column("status", user_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("pro_expire_time", sa.DateTime(), nullable=True),
        sa.Column("pro_order_no", sa.String(length=64), nullable=True),
        sa.Column("sms_code", sa.String(length=6), nullable=True),
        sa.Column("sms_code_expire", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("last_login_ip", sa.String(length=45), nullable=True),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
    )
    op.create_index("idx_user_phone", "users", ["phone"])
    op.create_index("idx_user_created_at", "users", ["created_at"])
    op.create_index("idx_user_role", "users", ["role"])

    op.create_table(
        "sms_codes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("phone", sa.String(length=11), nullable=False),
        sa.Column("code", sa.String(length=6), nullable=False),
        sa.Column("purpose", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expire_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_sms_code_phone", "sms_codes", ["phone", "purpose"])
    op.create_index("idx_sms_code_expire", "sms_codes", ["expire_at"])

    op.create_table(
        "login_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("phone", sa.String(length=11), nullable=False),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("device", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_login_log_phone", "login_logs", ["phone"])
    op.create_index("idx_login_log_created_at", "login_logs", ["created_at"])

    op.create_table(
        "design_projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("house_type", sa.String(length=20), nullable=True),
        sa.Column("area", sa.Integer(), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("layout_image", sa.String(length=500), nullable=True),
        sa.Column("layout_data", sa.JSON(), nullable=True),
        sa.Column("style", design_style_enum, nullable=True),
        sa.Column("layout_type", layout_type_enum, nullable=True),
        sa.Column("layouts", sa.JSON(), nullable=True),
        sa.Column("selected_layout", sa.JSON(), nullable=True),
        sa.Column("render_images", sa.JSON(), nullable=True),
        sa.Column("construction_drawings", sa.JSON(), nullable=True),
        sa.Column("material_list", sa.JSON(), nullable=True),
        sa.Column("status", design_status_enum, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_design_user", "design_projects", ["user_id"])
    op.create_index("idx_design_status", "design_projects", ["status"])

    op.create_table(
        "budget_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("space", sa.String(length=50), nullable=True),
        sa.Column("item_name", sa.String(length=100), nullable=False),
        sa.Column("spec", sa.String(length=200), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit_price", sa.Integer(), nullable=True),
        sa.Column("total_price", sa.Integer(), nullable=True),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("material", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_budget_project", "budget_items", ["project_id"])

    op.create_table(
        "budget_summaries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("material_cost", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("labor_cost", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("management_fee", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("misc_cost", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_cost", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("budget_limit", sa.Integer(), nullable=True),
        sa.Column("is_over_budget", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("over_amount", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("project_id", name="uq_budget_summaries_project_id"),
    )
    op.create_index("idx_budget_summary_project", "budget_summaries", ["project_id"])

    op.create_table(
        "inspection_reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("house_type", sa.String(length=20), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("district", sa.String(length=50), nullable=True),
        sa.Column("area", sa.Integer(), nullable=True),
        sa.Column("layout_image", sa.String(length=500), nullable=True),
        sa.Column("room_images", sa.JSON(), nullable=True),
        sa.Column("status", inspection_status_enum, nullable=True),
        sa.Column("ai_result", sa.JSON(), nullable=True),
        sa.Column("issues", sa.JSON(), nullable=True),
        sa.Column("high_risk_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("medium_risk_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("low_risk_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("report_url", sa.String(length=500), nullable=True),
        sa.Column("report_content", sa.Text(), nullable=True),
        sa.Column("city_risks", sa.JSON(), nullable=True),
        sa.Column("review_status", sa.String(length=20), nullable=True, server_default="pending"),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("reviewer_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_inspection_user", "inspection_reports", ["user_id"])
    op.create_index("idx_inspection_status", "inspection_reports", ["status"])
    op.create_index("idx_inspection_created", "inspection_reports", ["created_at"])

    op.create_table(
        "house_issues",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("report_id", sa.String(length=36), nullable=False),
        sa.Column("issue_type", sa.String(length=50), nullable=False),
        sa.Column("issue_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("position_detail", sa.String(length=200), nullable=True),
        sa.Column("risk_level", inspection_risk_level_enum, nullable=True),
        sa.Column("severity", sa.Integer(), nullable=True, server_default="5"),
        sa.Column("suggestion", sa.Text(), nullable=True),
        sa.Column("estimated_cost", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("image_coords", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_issue_report", "house_issues", ["report_id"])
    op.create_index("idx_issue_type", "house_issues", ["issue_type"])

    op.create_table(
        "construction_projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("design_project_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("area", sa.Integer(), nullable=True),
        sa.Column("total_cycle", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("actual_end_date", sa.DateTime(), nullable=True),
        sa.Column("status", construction_status_enum, nullable=True),
        sa.Column("progress", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("plan", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_construction_user", "construction_projects", ["user_id"])
    op.create_index("idx_construction_status", "construction_projects", ["status"])

    op.create_table(
        "construction_nodes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("node_type", sa.String(length=50), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("standard_days", sa.Integer(), nullable=True, server_default="7"),
        sa.Column("planned_start", sa.DateTime(), nullable=True),
        sa.Column("planned_end", sa.DateTime(), nullable=True),
        sa.Column("actual_start", sa.DateTime(), nullable=True),
        sa.Column("actual_end", sa.DateTime(), nullable=True),
        sa.Column("status", node_status_enum, nullable=True),
        sa.Column("acceptance_status", sa.String(length=20), nullable=True, server_default="pending"),
        sa.Column("acceptance_comment", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("standards", sa.Text(), nullable=True),
        sa.Column("warning_level", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_node_project", "construction_nodes", ["project_id"])
    op.create_index("idx_node_status", "construction_nodes", ["status"])

    op.create_table(
        "site_photos",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("node_id", sa.String(length=36), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("recognized_node", sa.String(length=50), nullable=True),
        sa.Column("progress_percentage", sa.Integer(), nullable=True),
        sa.Column("is_normal", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("abnormal_issues", sa.JSON(), nullable=True),
        sa.Column("uploaded_by", sa.String(length=36), nullable=False),
        sa.Column("uploader_type", sa.String(length=20), nullable=True, server_default="user"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_photo_project", "site_photos", ["project_id"])
    op.create_index("idx_photo_node", "site_photos", ["node_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("order_no", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("product_type", sa.String(length=50), nullable=False),
        sa.Column("product_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", order_status_enum, nullable=True),
        sa.Column("payment_method", payment_method_enum, nullable=True),
        sa.Column("payment_time", sa.DateTime(), nullable=True),
        sa.Column("wechat_order_no", sa.String(length=64), nullable=True),
        sa.Column("expire_days", sa.Integer(), nullable=True, server_default="180"),
        sa.Column("effective_time", sa.DateTime(), nullable=True),
        sa.Column("expire_time", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("order_no", name="uq_orders_order_no"),
    )
    op.create_index("idx_order_user", "orders", ["user_id"])
    op.create_index("idx_order_status", "orders", ["status"])
    op.create_index("idx_order_no", "orders", ["order_no"])

    op.create_table(
        "payment_callbacks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("order_id", sa.String(length=36), nullable=False),
        sa.Column("callback_type", sa.String(length=20), nullable=False),
        sa.Column("callback_data", sa.JSON(), nullable=True),
        sa.Column("callback_status", sa.String(length=20), nullable=True, server_default="pending"),
        sa.Column("process_result", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_callback_order", "payment_callbacks", ["order_id"])


def downgrade() -> None:
    op.drop_index("idx_callback_order", table_name="payment_callbacks")
    op.drop_table("payment_callbacks")
    op.drop_index("idx_order_no", table_name="orders")
    op.drop_index("idx_order_status", table_name="orders")
    op.drop_index("idx_order_user", table_name="orders")
    op.drop_table("orders")
    op.drop_index("idx_photo_node", table_name="site_photos")
    op.drop_index("idx_photo_project", table_name="site_photos")
    op.drop_table("site_photos")
    op.drop_index("idx_node_status", table_name="construction_nodes")
    op.drop_index("idx_node_project", table_name="construction_nodes")
    op.drop_table("construction_nodes")
    op.drop_index("idx_construction_status", table_name="construction_projects")
    op.drop_index("idx_construction_user", table_name="construction_projects")
    op.drop_table("construction_projects")
    op.drop_index("idx_issue_type", table_name="house_issues")
    op.drop_index("idx_issue_report", table_name="house_issues")
    op.drop_table("house_issues")
    op.drop_index("idx_inspection_created", table_name="inspection_reports")
    op.drop_index("idx_inspection_status", table_name="inspection_reports")
    op.drop_index("idx_inspection_user", table_name="inspection_reports")
    op.drop_table("inspection_reports")
    op.drop_index("idx_budget_summary_project", table_name="budget_summaries")
    op.drop_table("budget_summaries")
    op.drop_index("idx_budget_project", table_name="budget_items")
    op.drop_table("budget_items")
    op.drop_index("idx_design_status", table_name="design_projects")
    op.drop_index("idx_design_user", table_name="design_projects")
    op.drop_table("design_projects")
    op.drop_index("idx_login_log_created_at", table_name="login_logs")
    op.drop_index("idx_login_log_phone", table_name="login_logs")
    op.drop_table("login_logs")
    op.drop_index("idx_sms_code_expire", table_name="sms_codes")
    op.drop_index("idx_sms_code_phone", table_name="sms_codes")
    op.drop_table("sms_codes")
    op.drop_index("idx_user_role", table_name="users")
    op.drop_index("idx_user_created_at", table_name="users")
    op.drop_index("idx_user_phone", table_name="users")
    op.drop_table("users")

    # Drop enums (created implicitly by SQLAlchemy during CREATE TABLE)
    op.execute("DROP TYPE IF EXISTS paymentmethod")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS nodestatus")
    op.execute("DROP TYPE IF EXISTS constructionstatus")
    op.execute("DROP TYPE IF EXISTS inspectionrisklevel")
    op.execute("DROP TYPE IF EXISTS inspectionstatus")
    op.execute("DROP TYPE IF EXISTS designstatus")
    op.execute("DROP TYPE IF EXISTS layouttype")
    op.execute("DROP TYPE IF EXISTS designstyle")
    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
