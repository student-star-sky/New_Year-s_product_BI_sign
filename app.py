import json
import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from flask import Flask, send_from_directory, redirect
import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
from flask import Flask, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from config import Config
from models import db, Product
from auth import auth_bp, bcrypt
from data_loader import load_csv_to_db

# ---------- 创建Flask应用 ----------
server = Flask(__name__)
server.config.from_object(Config)

# ---------- 确保必要目录存在 ----------
os.makedirs('instance', exist_ok=True)   # SQLite数据库目录
os.makedirs('logs', exist_ok=True)       # 日志目录
os.makedirs('templates', exist_ok=True)  # 静态页面目录（用于登录页）

# ---------- 日志配置 ----------
file_handler = RotatingFileHandler(
    server.config['LOG_FILE'],
    maxBytes=server.config['LOG_MAX_BYTES'],
    backupCount=server.config['LOG_BACKUP_COUNT']
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(server.config['LOG_LEVEL'])
server.logger.addHandler(file_handler)
server.logger.setLevel(server.config['LOG_LEVEL'])

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
server.logger.addHandler(console_handler)

server.logger.info('Application started')

# ---------- 初始化扩展 ----------
db.init_app(server)
bcrypt.init_app(server)
jwt = JWTManager(server)

# ---------- 注册认证蓝图 ----------
server.register_blueprint(auth_bp, url_prefix='/auth')

# ---------- 根路径重定向到 Dash 看板 ---------- # 🔁 新增
@server.route('/')
def index():
    return redirect('/auth/login-page')

# ---------- 可选：处理 favicon.ico 避免 404 日志 ---------- # 🔁 新增
@server.route('/favicon.ico')
def favicon():
    return '', 204  # 无内容，状态码 204 No Content

# ---------- 创建Dash应用 ----------
app = dash.Dash(__name__, server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                url_base_pathname='/dashboard/')
app.title = 'Acceberg 商品分析BI'

# ---------- 加载中国GeoJSON ----------
GEOJSON_PATH = 'utils_file/china.geojson'
with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
    geojson = json.load(f)
FEATURE_ID_KEY = 'properties.name'   # 根据实际字段调整

# ---------- 辅助函数：从数据库获取真实数据 ----------
def get_kpi_data():
    total_sales = db.session.query(db.func.sum(Product.chengjiaov)).scalar() or 0
    total_orders = db.session.query(db.func.sum(Product.saleVolume)).scalar() or 0
    total_visitors = 7324  # 演示数据
    conversion = 4.2
    return total_sales, total_orders, total_visitors, conversion

# ---------- 前端JWT认证集成 ----------
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    # 这里可以添加JWT认证检查逻辑
    # 前端通过localStorage存储token，实际项目中可以通过API验证token
    
    if pathname in ('/dashboard/', '/dashboard'):
        return render_dashboard()
    elif pathname == '/dashboard/products':
        return render_product_analysis()
    elif pathname == '/dashboard/users':
        return render_user_analysis()
    elif pathname == '/dashboard/ads':
        return render_ad_analysis()
    elif pathname == '/dashboard/system':
        return render_system_management()
    return render_dashboard()

def render_user_analysis():
    """用户分析页面"""
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("用户分析"), width=12)
        ], className="mb-4"),
        
        dbc.Card([
            dbc.CardBody([
                html.P("用户分析页面开发中..."),
                html.P("这里将显示用户注册趋势、活跃度分析等数据")
            ])
        ])
    ], fluid=True)

def render_ad_analysis():
    """广告分析页面"""
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("广告分析"), width=12)
        ], className="mb-4"),
        
        dbc.Card([
            dbc.CardBody([
                html.P("广告分析页面开发中..."),
                html.P("这里将显示广告投放效果、转化率分析等数据")
            ])
        ])
    ], fluid=True)

def render_system_management():
    """系统管理页面"""
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("系统管理"), width=12)
        ], className="mb-4"),
        
        dbc.Card([
            dbc.CardBody([
                html.P("系统管理页面开发中..."),
                html.P("这里将显示系统配置、用户权限管理等功能")
            ])
        ])
    ], fluid=True)

def get_sales_trend():
    # 模拟7天销售数据（实际项目中应从数据库按日期查询）
    dates = [(datetime.today() - timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]
    
    # 基于真实商品数据计算平均销售额
    total_sales = db.session.query(db.func.sum(Product.chengjiaov)).scalar() or 1000
    avg_daily_sales = total_sales / 7
    
    # 生成基于真实数据的趋势
    sales = [int(avg_daily_sales * (0.8 + np.random.random() * 0.4)) for _ in range(7)]
    orders = [int(s * 10) for s in sales]  # 假设平均客单价0.1万
    
    df = pd.DataFrame({
        '日期': dates,
        '销售额(万)': sales,
        '订单量(千)': orders
    })
    return df

def get_province_sales():
    # 基于真实商品数据的省级分布（模拟）
    provinces_with_data = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '山东省',
                           '河南省', '湖北省', '湖南省', '四川省', '重庆市']
    
    total_sales = db.session.query(db.func.sum(Product.chengjiaov)).scalar() or 5000
    province_sales = []
    remaining_sales = total_sales
    
    for i, province in enumerate(provinces_with_data):
        if i == len(provinces_with_data) - 1:
            sales = remaining_sales
        else:
            sales = int(total_sales * (0.05 + np.random.random() * 0.2))
            remaining_sales -= sales
        province_sales.append(sales)
    
    return pd.DataFrame({'省份': provinces_with_data, '销售额(万)': province_sales})

def get_product_category_stats():
    counts = db.session.query(
        Product.category,
        db.func.count(Product.id)
    ).group_by(Product.category).all()
    df = pd.DataFrame(counts, columns=['category', 'count'])
    return df

def get_top_companies():
    companies = db.session.query(
        Product.company,
        db.func.sum(Product.chengjiaov).label('total_sales')
    ).group_by(Product.company).order_by(db.desc('total_sales')).limit(10).all()
    df = pd.DataFrame(companies, columns=['company', 'total_sales'])
    return df

# ---------- Dash布局 ----------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("过年商品分析看板", className="text-primary fw-bold"), width=6),
        dbc.Col(html.Div(id='login-status', className="text-end mt-3"), width=6)
    ], className="mt-3 mb-2"),

    dbc.Row([
        dbc.Col([
            html.H5("导航菜单", className="fw-bold mb-3"),
            dbc.Nav([
                dbc.NavLink("📊 行为分析", href="/dashboard/", active="exact"),
                dbc.NavLink("👥 用户分析", href="/dashboard/users", active="exact"),
                dbc.NavLink("📦 商品分析", href="/dashboard/products", active="exact"),
                dbc.NavLink("📢 广告分析", href="/dashboard/ads", active="exact"),
                dbc.NavLink("⚙️ 系统管理", href="/dashboard/system", active="exact"),
            ], vertical=True, pills=True, className="gap-2")
        ], width=2),

        dbc.Col([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ], width=10)
    ])
], fluid=True)



def render_dashboard():
    total_sales, total_orders, visitors, conversion = get_kpi_data()
    df_trend = get_sales_trend()
    df_province = get_province_sales()
    df_category = get_product_category_stats()
    df_top_companies = get_top_companies()

    fig_map = build_map(df_province)
    fig_sales_trend = px.line(df_trend, x='日期', y='销售额(万)', markers=True, height=250)
    fig_orders_trend = px.line(df_trend, x='日期', y='订单量(千)', markers=True, height=250)
    fig_category_pie = px.pie(df_category, names='category', values='count', title='各品类商品数占比')
    fig_company_bar = px.bar(df_top_companies, x='company', y='total_sales', title='公司成交额TOP10')

    return dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("总销售额 (万元)", className="card-title text-secondary"),
                    html.H3(f"{total_sales:,.2f}", className="card-text fw-bold"),
                ])
            ], color="light", className="shadow-sm"), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("总销量 (件)", className="card-title text-secondary"),
                    html.H3(f"{total_orders:,}", className="card-text fw-bold"),
                ])
            ], color="light", className="shadow-sm"), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("访客数 (人)", className="card-title text-secondary"),
                    html.H3(f"{visitors:,}", className="card-text fw-bold"),
                ])
            ], color="light", className="shadow-sm"), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("转化率 (%)", className="card-title text-secondary"),
                    html.H3(f"{conversion}%", className="card-text fw-bold"),
                ])
            ], color="light", className="shadow-sm"), width=3),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("📈 7日销售额趋势"),
                dbc.CardBody(dcc.Graph(figure=fig_sales_trend))
            ]), width=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader("📊 7日订单量趋势"),
                dbc.CardBody(dcc.Graph(figure=fig_orders_trend))
            ]), width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("🗺️ 省级销售额分布"),
                dbc.CardBody(dcc.Graph(figure=fig_map))
            ]), width=7),
            dbc.Col(dbc.Card([
                dbc.CardHeader("🥧 品类占比"),
                dbc.CardBody([
                    dcc.Graph(figure=fig_category_pie),
                    html.Div(id='category-stats', className="mt-3")
                ])
            ]), width=5),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("🏢 公司成交额TOP10"),
                dbc.CardBody(dcc.Graph(figure=fig_company_bar))
            ]), width=12)
        ])
    ], fluid=True)

def render_product_analysis():
    # 获取商品数据
    products = db.session.query(Product).all()
    
    # 构建商品分析页面
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("商品分析"), width=8),
            dbc.Col(dbc.Button("导出数据", color="primary", className="float-end"), width=4)
        ], className="mb-4"),
        
        # 筛选区域
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("品类筛选"),
                        dcc.Dropdown(
                            id='category-filter',
                            options=[
                                {'label': '全部', 'value': 'all'},
                                {'label': '羽绒服', 'value': 'DownJacket'},
                                {'label': '烧烤食材', 'value': 'BBQ'},
                                {'label': '年货', 'value': 'Year'}
                            ],
                            value='all',
                            className="mb-3"
                        )
                    ], width=3),
                    dbc.Col([
                        html.Label("价格区间"),
                        dcc.RangeSlider(
                            id='price-range',
                            min=0,
                            max=1000,
                            step=50,
                            value=[0, 1000],
                            marks={0: '0', 200: '200', 400: '400', 600: '600', 800: '800', 1000: '1000'},
                            className="mb-3"
                        )
                    ], width=5),
                    dbc.Col([
                        html.Label("销量排序"),
                        dcc.RadioItems(
                            id='sort-by',
                            options=[
                                {'label': '销售额', 'value': 'sales'},
                                {'label': '销量', 'value': 'volume'},
                                {'label': '价格', 'value': 'price'}
                            ],
                            value='sales',
                            inline=True,
                            className="mb-3"
                        )
                    ], width=4)
                ])
            ])
        ], className="mb-4"),
        
        # 商品列表
        dbc.Card([
            dbc.CardHeader("商品列表"),
            dbc.CardBody([
                html.Div(id='product-table', className="overflow-x-auto")
            ])
        ], className="mb-4"),
        
        # 商品分析图表
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("价格分布"),
                dbc.CardBody(dcc.Graph(id='price-distribution'))
            ]), width=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader("销量与销售额关系"),
                dbc.CardBody(dcc.Graph(id='sales-volume-scatter'))
            ]), width=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("品类销售额对比"),
                dbc.CardBody(dcc.Graph(id='category-sales'))
            ]), width=12)
        ])
    ], fluid=True)

def build_map(df_province):
    fig = go.Figure()
    
    # 创建省份销售数据字典
    province_sales = {}
    for _, row in df_province.iterrows():
        province_sales[row['省份']] = row['销售额(万)']
    
    # 准备所有省份的数据
    all_provinces = []
    all_values = []
    
    for feat in geojson['features']:
        province_name = feat['properties']['name']
        all_provinces.append(province_name)
        all_values.append(province_sales.get(province_name, 0))
    
    # 添加热力图层
    fig.add_trace(go.Choropleth(
        geojson=geojson,
        locations=all_provinces,
        z=all_values,
        featureidkey=FEATURE_ID_KEY,
        colorscale='Reds',
        showscale=True,
        colorbar_title='销售额(万元)',
        marker_line_width=0.8,
        marker_line_color='gray',
        hoverinfo='z+location',
        name='销售额'
    ))
    
    # 优化地图显示
    fig.update_geos(
        lataxis_range=[15, 55],
        lonaxis_range=[70, 140],
        landcolor='whitesmoke',
        countrycolor='gray',
        coastlinecolor='gray',
        showcountries=False,
        showcoastlines=True,
        showland=True,
        fitbounds="locations",
        visible=True
    )
    
    # 优化布局
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=400,
        showlegend=False,
        geo=dict(
            projection_scale=5,
            center=dict(lat=35, lon=105)
        )
    )
    
    return fig

# ---------- 商品分析页面回调 ----------
@app.callback(
    Output('product-table', 'children'),
    [Input('category-filter', 'value'),
     Input('price-range', 'value'),
     Input('sort-by', 'value')]
)
def update_product_table(category, price_range, sort_by):
    # 构建查询
    query = db.session.query(Product)
    
    # 品类筛选
    if category != 'all':
        query = query.filter(Product.category == category)
    
    # 价格区间筛选
    min_price, max_price = price_range
    query = query.filter(Product.price >= min_price, Product.price <= max_price)
    
    # 排序
    if sort_by == 'sales':
        query = query.order_by(db.desc(Product.chengjiaov))
    elif sort_by == 'volume':
        query = query.order_by(db.desc(Product.saleVolume))
    elif sort_by == 'price':
        query = query.order_by(db.desc(Product.price))
    
    products = query.limit(50).all()
    
    # 构建表格
    table_rows = []
    for product in products:
        table_rows.append(
            html.Tr([
                html.Td(product.id),
                html.Td(product.company),
                html.Td(product.subject[:50] + '...' if len(product.subject) > 50 else product.subject),
                html.Td(f"¥{product.price}"),
                html.Td(product.saleVolume),
                html.Td(f"{product.chengjiaov}万"),
                html.Td(product.category),
                html.Td(html.A("查看", href=product.odUrl, target="_blank"))
            ])
        )
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th("ID"),
            html.Th("公司"),
            html.Th("商品标题"),
            html.Th("价格"),
            html.Th("销量"),
            html.Th("销售额"),
            html.Th("品类"),
            html.Th("操作")
        ])),
        html.Tbody(table_rows)
    ], className="table table-striped table-hover")

@app.callback(
    Output('price-distribution', 'figure'),
    [Input('category-filter', 'value')]
)
def update_price_distribution(category):
    query = db.session.query(Product)
    if category != 'all':
        query = query.filter(Product.category == category)
    
    products = query.all()
    prices = [p.price for p in products if p.price > 0]
    
    fig = px.histogram(prices, nbins=20, title="商品价格分布")
    fig.update_layout(xaxis_title="价格", yaxis_title="商品数量")
    return fig

@app.callback(
    Output('sales-volume-scatter', 'figure'),
    [Input('category-filter', 'value')]
)
def update_sales_volume_scatter(category):
    query = db.session.query(Product)
    if category != 'all':
        query = query.filter(Product.category == category)
    
    products = query.all()
    data = [
        {'volume': p.saleVolume, 'sales': p.chengjiaov, 'category': p.category}
        for p in products if p.saleVolume > 0 and p.chengjiaov > 0
    ]
    
    df = pd.DataFrame(data)
    fig = px.scatter(df, x='volume', y='sales', color='category',
                    title="销量与销售额关系")
    fig.update_layout(xaxis_title="销量", yaxis_title="销售额（万元）")
    return fig

@app.callback(
    Output('category-sales', 'figure'),
    [Input('category-filter', 'value')]
)
def update_category_sales(category):
    query = db.session.query(
        Product.category,
        db.func.sum(Product.chengjiaov).label('total_sales')
    )
    
    if category != 'all':
        query = query.filter(Product.category == category)
    
    results = query.group_by(Product.category).all()
    data = [{'category': r.category, 'sales': r.total_sales} for r in results]
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x='category', y='sales', title="各品类销售额对比")
    fig.update_layout(xaxis_title="品类", yaxis_title="销售额（万元）")
    return fig

# 品类统计信息回调
@app.callback(
    Output('category-stats', 'children'),
    Input('url', 'pathname')
)
def update_category_stats(pathname):
    # 获取各品类的详细统计
    stats = db.session.query(
        Product.category,
        db.func.count(Product.id).label('count'),
        db.func.sum(Product.chengjiaov).label('total_sales'),
        db.func.sum(Product.saleVolume).label('total_volume'),
        db.func.avg(Product.price).label('avg_price')
    ).group_by(Product.category).all()
    
    stats_items = []
    for stat in stats:
        stats_items.append(
            dbc.ListGroupItem([
                html.Span(f"{stat.category}: ", className="font-weight-bold"),
                html.Span(f"商品数: {stat.count}, "),
                html.Span(f"销售额: {stat.total_sales:.2f}万, "),
                html.Span(f"销量: {stat.total_volume}, "),
                html.Span(f"均价: ¥{stat.avg_price:.2f}")
            ])
        )
    
    return dbc.ListGroup(stats_items, flush=True)

# ---------- 登录状态显示回调 ----------
@app.callback(
    Output('login-status', 'children'),
    Input('url', 'pathname')
)
def update_login_status(pathname):
    # 前端通过localStorage存储token，这里返回JS代码让前端动态更新
    return html.Span([
        html.Script('''
            function updateLoginStatus() {
                const username = localStorage.getItem('username');
                const statusElement = document.getElementById('login-status');
                
                if (username) {
                    statusElement.innerHTML = `
                        <span class="me-3">欢迎，${username}</span>
                        <button onclick="logout()" class="btn btn-sm btn-outline-danger">注销</button>
                    `;
                } else {
                    statusElement.innerHTML = `
                        <a href="/auth/login-page" class="me-2">登录</a>
                        <a href="/auth/register-page">注册</a>
                    `;
                }
            }
            
            function logout() {
                localStorage.removeItem('access_token');
                localStorage.removeItem('username');
                updateLoginStatus();
                // 可选：跳转到登录页
                // window.location.href = '/auth/login-page';
            }
            
            // 初始化时更新状态
            updateLoginStatus();
        '''),
        html.Span(id='login-status-content')
    ])

# ---------- 静态文件路由（用于登录页面）----------
@server.route('/auth/<path:filename>')
def auth_static(filename):
    return send_from_directory('templates', filename)

# ---------- 静态文件路由（用于视频背景）----------
@server.route('/utils_file/<path:filename>')
def utils_static(filename):
    import urllib.parse
    filename = urllib.parse.unquote(filename)
    return send_from_directory('utils_file', filename)

# ---------- 启动时初始化数据库 ----------
if __name__ == '__main__':
    with server.app_context():
        db.create_all()
        # 检查是否已有数据
        if Product.query.first() is None:
            server.logger.info("Importing data...")
            load_csv_to_db('product_BBQ.csv', 'BBQ')
            load_csv_to_db('product_down_jacket.csv', 'DownJacket')
            load_csv_to_db('product_Year.csv', 'Year')
            server.logger.info("Data imported successfully!")
        else:
            server.logger.info("Database already contains data, skipping import.")
    # server.run(debug=True, host='0.0.0.0', port=5000)