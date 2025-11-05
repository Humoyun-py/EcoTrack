from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import BlogPost, PostLike, PostComment
from datetime import datetime

blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

@blog_bp.route('/')
def blog_index():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(is_published=True)\
        .order_by(BlogPost.created_at.desc())\
        .paginate(page=page, per_page=6)
    return render_template('blog/blog.html', posts=posts)

@blog_bp.route('/post/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('blog/blog_post.html', post=post)

@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def blog_create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        post = BlogPost(
            title=title,
            content=content,
            author_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post muvaffaqiyatli yaratildi!', 'success')
        return redirect(url_for('blog.blog_index'))
    
    return render_template('blog/blog_create.html')

@blog_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    existing_like = PostLike.query.filter_by(
        user_id=current_user.id, 
        post_id=post_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'liked': False, 'likes_count': PostLike.query.filter_by(post_id=post_id).count()})
    else:
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'liked': True, 'likes_count': PostLike.query.filter_by(post_id=post_id).count()})

@blog_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    
    comment = PostComment(
        content=content,
        user_id=current_user.id,
        post_id=post_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Izoh muvaffaqiyatli qo\'shildi!', 'success')
    return redirect(url_for('blog.blog_post', post_id=post_id))