"""
网站地图生成器
为搜索引擎提供网站结构信息
"""
from flask import url_for, request
from app.models import Category, Website, SiteSettings
from datetime import datetime
import xml.etree.ElementTree as ET


def generate_sitemap():
    """生成XML格式的网站地图"""
    # 创建根元素
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    urlset.set('xsi:schemaLocation', 'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')
    
    # 添加首页
    url_elem = ET.SubElement(urlset, 'url')
    ET.SubElement(url_elem, 'loc').text = url_for('main.index', _external=True)
    ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    ET.SubElement(url_elem, 'changefreq').text = 'daily'
    ET.SubElement(url_elem, 'priority').text = '1.0'
    
    # 添加分类页面
    categories = Category.query.filter_by(parent_id=None).all()
    for category in categories:
        # 主分类页面
        url_elem = ET.SubElement(urlset, 'url')
        ET.SubElement(url_elem, 'loc').text = url_for('main.category', id=category.id, _external=True)
        ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        ET.SubElement(url_elem, 'changefreq').text = 'weekly'
        ET.SubElement(url_elem, 'priority').text = '0.8'
        
        # 子分类页面
        for child in category.children:
            url_elem = ET.SubElement(urlset, 'url')
            ET.SubElement(url_elem, 'loc').text = url_for('main.category', id=child.id, _external=True)
            ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
            ET.SubElement(url_elem, 'changefreq').text = 'weekly'
            ET.SubElement(url_elem, 'priority').text = '0.7'
    
    # 添加公开的网站详情页（跳转页）
    public_websites = Website.query.filter_by(is_private=False).all()
    for website in public_websites:
        url_elem = ET.SubElement(urlset, 'url')
        ET.SubElement(url_elem, 'loc').text = url_for('main.site', id=website.id, _external=True)
        # Website 没有 updated_at 字段，使用最后访问时间或创建时间
        lastmod_dt = website.last_view or website.created_at
        ET.SubElement(url_elem, 'lastmod').text = lastmod_dt.strftime('%Y-%m-%d') if lastmod_dt else datetime.now().strftime('%Y-%m-%d')
        ET.SubElement(url_elem, 'changefreq').text = 'monthly'
        ET.SubElement(url_elem, 'priority').text = '0.6'
    
    # 添加搜索页面
    url_elem = ET.SubElement(urlset, 'url')
    ET.SubElement(url_elem, 'loc').text = url_for('main.search', _external=True)
    ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    ET.SubElement(url_elem, 'changefreq').text = 'weekly'
    ET.SubElement(url_elem, 'priority').text = '0.5'
    
    # 添加关于页面（如果存在）
    try:
        about_url = url_for('main.about', _external=True)
    except Exception:
        about_url = None
    if about_url:
        url_elem = ET.SubElement(urlset, 'url')
        ET.SubElement(url_elem, 'loc').text = about_url
        ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        ET.SubElement(url_elem, 'changefreq').text = 'monthly'
        ET.SubElement(url_elem, 'priority').text = '0.3'
    
    # 转换为字符串
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ", level=0)  # 格式化XML
    
    return tree


def generate_robots_txt():
    """生成robots.txt内容"""
    robots_content = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {url_for('main.sitemap', _external=True)}

# 禁止爬取管理页面
Disallow: /admin/
Disallow: /auth/
Disallow: /api/

# 禁止爬取私有内容
Disallow: /*?private=*
Disallow: /private/

# 爬取延迟（毫秒）
Crawl-delay: 1
"""
    return robots_content
