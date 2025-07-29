# Flask 学习笔记 - 数据库 (Define and Access the Database)

## 概述

应用将使用SQLite数据库来存储用户和文章。Python内置了对SQLite的支持，通过`sqlite3`模块。

**SQLite的优势：**
- 不需要设置单独的数据库服务器
- Python内置支持
- 适合中小型应用
- 零配置，开箱即用

**注意事项：**
- 并发写入请求会按顺序执行，可能变慢
- 小型应用不会注意到这个问题
- 应用变大时可能需要切换到其他数据库

## 数据库连接

### 核心概念

在Web应用中，数据库连接通常与请求绑定：
- 在处理请求时创建连接
- 在发送响应前关闭连接
- 使用Flask的`g`对象存储连接

### 代码实现

```python
import sqlite3
from datetime import datetime
import click
from flask import current_app, g

def get_db():
    """
    获取数据库连接
    - 如果当前请求中没有数据库连接，创建一个新的
    - 使用g对象存储连接，确保同一请求中复用
    - 设置row_factory为sqlite3.Row，使结果行像字典一样访问
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """
    关闭数据库连接
    - 检查g.db是否存在
    - 如果存在则关闭连接
    - 从g对象中移除连接
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()
```

### 重要概念解释

#### 1. `g` 对象
- 每个请求唯一的特殊对象
- 用于存储请求期间多个函数可能访问的数据
- 连接被存储和重用，而不是每次调用都创建新连接

#### 2. `current_app`
- 指向处理请求的Flask应用的特殊对象
- 由于使用应用工厂，编写代码时没有应用对象
- `get_db`在应用创建并处理请求时调用，所以可以使用`current_app`

#### 3. `sqlite3.Row`
- 告诉连接返回行为像字典的行
- 允许通过名称访问列：`row['username']`而不是`row[0]`

## 创建数据库表

### 数据库模式 (schema.sql)

```sql
-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

-- 用户表
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
  username TEXT UNIQUE NOT NULL,         -- 用户名，唯一，不能为空
  password TEXT NOT NULL                 -- 密码，不能为空
);

-- 文章表
CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
  author_id INTEGER NOT NULL,            -- 作者ID，外键
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间，默认当前时间
  title TEXT NOT NULL,                   -- 标题，不能为空
  body TEXT NOT NULL,                    -- 内容，不能为空
  FOREIGN KEY (author_id) REFERENCES user (id)  -- 外键约束
);
```

### 初始化数据库函数

```python
def init_db():
    """
    初始化数据库
    - 获取数据库连接
    - 读取schema.sql文件
    - 执行SQL脚本创建表
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """
    命令行命令：初始化数据库
    - 清除现有数据并创建新表
    - 显示成功消息
    """
    init_db()
    click.echo('Initialized the database.')

# 注册时间戳转换器
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)
```

## 注册到应用

```python
def init_app(app):
    """
    将数据库函数注册到应用
    - 注册close_db为应用上下文清理函数
    - 添加init-db命令行命令
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
```

### 在应用工厂中注册

```python
# flaskr/__init__.py
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # ... 其他配置代码 ...

    # 注册数据库
    from . import db
    db.init_app(app)

    return app
```

## 实用SQLite3操作指南

### 1. 基础CRUD操作

#### 插入数据 (Create)
```python
def create_user(username, password):
    """创建用户"""
    db = get_db()
    try:
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, password)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        # 用户名已存在
        return False

def create_post(title, body, author_id):
    """创建文章"""
    db = get_db()
    db.execute(
        'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
        (title, body, author_id)
    )
    db.commit()
```

#### 查询数据 (Read)
```python
def get_user_by_id(user_id):
    """根据ID获取用户"""
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    return user

def get_user_by_username(username):
    """根据用户名获取用户"""
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    return user

def get_all_posts():
    """获取所有文章（带作者信息）"""
    db = get_db()
    posts = db.execute('''
        SELECT p.id, p.title, p.body, p.created, p.author_id, u.username
        FROM post p JOIN user u ON p.author_id = u.id
        ORDER BY p.created DESC
    ''').fetchall()
    return posts

def get_posts_by_user(user_id):
    """获取指定用户的文章"""
    db = get_db()
    posts = db.execute(
        'SELECT * FROM post WHERE author_id = ? ORDER BY created DESC',
        (user_id,)
    ).fetchall()
    return posts
```

#### 更新数据 (Update)
```python
def update_post(post_id, title, body, author_id):
    """更新文章"""
    db = get_db()
    db.execute(
        'UPDATE post SET title = ?, body = ? WHERE id = ? AND author_id = ?',
        (title, body, post_id, author_id)
    )
    db.commit()

def update_user_password(user_id, new_password):
    """更新用户密码"""
    db = get_db()
    db.execute(
        'UPDATE user SET password = ? WHERE id = ?',
        (new_password, user_id)
    )
    db.commit()
```

#### 删除数据 (Delete)
```python
def delete_post(post_id, author_id):
    """删除文章（只能删除自己的文章）"""
    db = get_db()
    db.execute(
        'DELETE FROM post WHERE id = ? AND author_id = ?',
        (post_id, author_id)
    )
    db.commit()

def delete_user(user_id):
    """删除用户（需要先删除相关文章）"""
    db = get_db()
    # 先删除用户的文章
    db.execute('DELETE FROM post WHERE author_id = ?', (user_id,))
    # 再删除用户
    db.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.commit()
```

### 2. 高级查询技巧

#### 分页查询
```python
def get_posts_paginated(page=1, per_page=10):
    """分页获取文章"""
    db = get_db()
    offset = (page - 1) * per_page
    
    posts = db.execute('''
        SELECT p.id, p.title, p.body, p.created, p.author_id, u.username
        FROM post p JOIN user u ON p.author_id = u.id
        ORDER BY p.created DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    
    return posts
```

#### 搜索功能
```python
def search_posts(keyword):
    """搜索文章"""
    db = get_db()
    keyword = f'%{keyword}%'
    
    posts = db.execute('''
        SELECT p.id, p.title, p.body, p.created, p.author_id, u.username
        FROM post p JOIN user u ON p.author_id = u.id
        WHERE p.title LIKE ? OR p.body LIKE ?
        ORDER BY p.created DESC
    ''', (keyword, keyword)).fetchall()
    
    return posts
```

#### 统计查询
```python
def get_user_stats(user_id):
    """获取用户统计信息"""
    db = get_db()
    stats = db.execute('''
        SELECT 
            COUNT(*) as post_count,
            MAX(created) as last_post_date,
            MIN(created) as first_post_date
        FROM post 
        WHERE author_id = ?
    ''', (user_id,)).fetchone()
    
    return stats

def get_popular_users(limit=5):
    """获取最活跃的用户"""
    db = get_db()
    users = db.execute('''
        SELECT u.username, COUNT(p.id) as post_count
        FROM user u LEFT JOIN post p ON u.id = p.author_id
        GROUP BY u.id, u.username
        ORDER BY post_count DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    
    return users
```

### 3. 事务处理

```python
def create_user_with_posts(username, password, posts_data):
    """创建用户并同时创建多篇文章（事务）"""
    db = get_db()
    try:
        # 开始事务
        db.execute('BEGIN')
        
        # 创建用户
        cursor = db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, password)
        )
        user_id = cursor.lastrowid
        
        # 创建文章
        for post in posts_data:
            db.execute(
                'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
                (post['title'], post['body'], user_id)
            )
        
        # 提交事务
        db.commit()
        return user_id
        
    except Exception as e:
        # 回滚事务
        db.rollback()
        raise e
```

### 4. 数据库连接池（高级用法）

```python
import sqlite3
from contextlib import contextmanager
from threading import local

class DatabaseManager:
    """数据库管理器（连接池）"""
    
    def __init__(self, database_path):
        self.database_path = database_path
        self._local = local()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.database_path,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self._local.connection.row_factory = sqlite3.Row
        
        try:
            yield self._local.connection
        except Exception:
            self._local.connection.rollback()
            raise
        finally:
            # 可选：关闭连接
            # self._local.connection.close()
            # delattr(self._local, 'connection')
            pass

# 使用示例
db_manager = DatabaseManager('path/to/database.sqlite')

def get_user_with_manager(user_id):
    """使用数据库管理器获取用户"""
    with db_manager.get_connection() as conn:
        user = conn.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        return user
```

## 初始化数据库

### 命令行初始化
```bash
flask --app flaskr init-db
```

### 预期输出