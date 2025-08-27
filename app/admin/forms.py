from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField, HiddenField, IntegerField, PasswordField, DateTimeField
from wtforms.validators import DataRequired, Length, URL, Optional, ValidationError, Email, EqualTo, NumberRange
from app.models import Category, User

class CategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('分类描述', validators=[Length(max=256)])
    icon = StringField('图标', validators=[Length(max=64)])
    color = StringField('颜色', validators=[Length(max=16)])
    order = IntegerField('排序', default=0)
    display_limit = IntegerField('首页展示数量', default=10)
    parent_id = SelectField('父分类', coerce=int, validators=[Optional()])
    submit_btn = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.parent_id.choices = [(0, '-- 无 --')] + [
            (c.id, c.name) for c in Category.query.filter(Category.parent_id.is_(None)).order_by(Category.order.desc()).all()
        ]
        
    def validate_parent_id(self, field):
        if field.data == 0:
            field.data = None

class WebsiteForm(FlaskForm):
    """添加/编辑网站表单"""
    title = StringField('网站名称', validators=[DataRequired(), Length(max=128)])
    url = StringField('网站URL', validators=[DataRequired(), URL(), Length(max=256)])
    description = TextAreaField('网站描述', validators=[Optional(), Length(max=512)])
    icon = StringField('图标URL', validators=[Optional(), Length(max=256)])
    category_id = SelectField('分类', coerce=int, validators=[DataRequired()])
    sort_order = IntegerField('排序权重', validators=[Optional(), NumberRange(min=0, max=9999)], 
                            default=0, description='值越大排序越靠前，默认为0')
    is_featured = BooleanField('推荐')
    is_private = BooleanField('设为私有')
    submit_btn = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(WebsiteForm, self).__init__(*args, **kwargs)
        def get_choices(categories, level=0):
            choices = []
            # 降序排列
            categories = sorted(categories, key=lambda x: x.order if hasattr(x, 'order') else 0, reverse=True)
            for c in categories:
                prefix = ''
                if level == 1:
                    prefix = '└─ '
                elif level > 1:
                    prefix = '　' * (level-1) + '└─ '
                choices.append((c.id, f"{prefix}{c.name}"))
                # 递归处理子分类，降序
                children = c.children.order_by(Category.order.desc()).all() if hasattr(c, 'children') else []
                if children:
                    choices.extend(get_choices(children, level+1))
            return choices

        # 只查顶级分类，递归生成choices，降序
        top_categories = Category.query.filter(Category.parent_id.is_(None)).order_by(Category.order.desc()).all()
        self.category_id.choices = get_choices(top_categories)

class InvitationForm(FlaskForm):
    count = IntegerField('生成数量', default=1, validators=[DataRequired()])
    submit_btn = SubmitField('生成邀请码')

class UserEditForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('电子邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    password = StringField('密码 (留空则不修改)', validators=[Optional(), Length(min=8, max=150)])
    is_admin = BooleanField('管理员权限')
    is_superadmin = BooleanField('超级管理员权限')
    submit_btn = SubmitField('保存')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('该用户名已被使用')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('该邮箱已被使用')

class SiteSettingsForm(FlaskForm):
    site_name = StringField('站点名称', validators=[DataRequired(), Length(max=128)])
    site_subtitle = StringField('站点副标题', validators=[Optional(), Length(max=256)])
    site_logo = StringField('站点Logo URL', validators=[Optional(), Length(max=256)])
    logo_file = FileField('上传Logo', validators=[FileAllowed(['jpg', 'png', 'gif', 'svg'], '只允许上传图片!')])
    site_favicon = StringField('站点图标URL', validators=[Optional(), Length(max=256)])
    favicon_file = FileField('上传Favicon', validators=[FileAllowed(['ico', 'png', 'jpg', 'svg'], '只允许上传图片!')])
    site_keywords = StringField('站点关键词', validators=[Optional(), Length(max=512)])
    site_description = TextAreaField('站点描述', validators=[Optional(), Length(max=1024)])
    footer_content = TextAreaField('页脚内容', validators=[Optional()])
    background_type = SelectField('背景类型', choices=[
        ('none', '无背景'),
        ('image', '图片背景'),
        ('gradient', '渐变色背景'),
        ('color', '纯色背景')
    ], validators=[Optional()])
    background_url = StringField('背景URL', validators=[Optional(), Length(max=512)])
    background_file = FileField('上传背景图片', validators=[FileAllowed(['jpg', 'png', 'gif', 'webp'], '只允许上传图片!')])
    
    # 过渡页设置
    enable_transition = BooleanField('启用过渡页')
    transition_time = IntegerField('访客停留时间', validators=[NumberRange(min=0, max=30)], default=5, description='设置为0则不显示过渡页直接跳转')
    admin_transition_time = IntegerField('管理员停留时间', validators=[NumberRange(min=0, max=30)], default=3, description='设置为0则不显示过渡页直接跳转')
    transition_ad1 = TextAreaField('广告1', validators=[Optional()])
    transition_ad2 = TextAreaField('广告2', validators=[Optional()])
    transition_remember_choice = BooleanField('允许用户选择不再显示')
    transition_show_description = BooleanField('显示网站描述')
    transition_theme = SelectField('主题风格', choices=[
        ('default', '默认主题'),
        ('minimal', '极简主题'),
        ('card', '卡片主题'),
        ('dark', '暗色主题')
    ], validators=[Optional()])
    transition_color = StringField('主色调', validators=[Optional(), Length(max=32)])
    
    # PC端背景设置
    pc_background_type = SelectField('PC端背景类型', choices=[
        ('none', '无背景'),
        ('image', '图片背景'),
        ('gradient', '渐变色背景'),
        ('color', '纯色背景')
    ], validators=[Optional()])
    pc_background_url = StringField('PC端背景URL', validators=[Optional(), Length(max=512)])
    pc_background_file = FileField('上传PC端背景图片', validators=[FileAllowed(['jpg', 'png', 'gif', 'webp'], '只允许上传图片!')])

    # 移动端背景设置
    mobile_background_type = SelectField('移动端背景类型', choices=[
        ('none', '无背景'),
        ('image', '图片背景'),
        ('gradient', '渐变色背景'),
        ('color', '纯色背景')
    ], validators=[Optional()])
    mobile_background_url = StringField('移动端背景URL', validators=[Optional(), Length(max=512)])
    mobile_background_file = FileField('上传移动端背景图片', validators=[FileAllowed(['jpg', 'png', 'gif', 'webp'], '只允许上传图片!')])
    
    # 公告设置
    announcement_enabled = BooleanField('启用公告')
    announcement_title = StringField('公告标题', validators=[Optional(), Length(max=128)])
    announcement_content = TextAreaField('公告内容', validators=[Optional()])
    announcement_start = DateTimeField('开始时间', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    announcement_end = DateTimeField('结束时间', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    announcement_remember_days = IntegerField('不再提示天数', validators=[Optional(), NumberRange(min=1, max=365)], default=7)
    
    submit_btn = SubmitField('保存设置')

class BackgroundForm(FlaskForm):
    title = StringField('背景名称', validators=[DataRequired(), Length(max=128)])
    url = StringField('背景URL', validators=[Optional(), Length(max=512)])
    type = SelectField('背景类型', choices=[
        ('image', '图片背景'),
        ('gradient', '渐变色背景'),
        ('color', '纯色背景')
    ], validators=[DataRequired()])
    device_type = SelectField('设备类型', choices=[
        ('pc', '电脑端'),
        ('mobile', '移动端'),
        ('both', '全部设备')
    ], validators=[DataRequired()])
    background_file = FileField('上传背景图片', validators=[FileAllowed(['jpg', 'png', 'gif', 'webp'], '只允许上传图片!')])
    submit_btn = SubmitField('保存背景')

class DataImportForm(FlaskForm):
    """数据导入表单"""
    db_file = FileField('数据库文件', validators=[
        DataRequired(),
        FileAllowed(['db', 'db3', 'sqlite', 'sqlite3'], '只允许上传SQLite数据库文件')
    ])
    import_type = SelectField('导入类型', choices=[
        ('merge', '合并 - 保留现有数据'),
        ('replace', '替换 - 清空现有数据')
    ])
    submit_btn = SubmitField('开始导入') 