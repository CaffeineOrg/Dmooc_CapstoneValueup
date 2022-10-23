from django.db import models


class Board(models.Model):
    title = models.CharField(max_length=64)
    contents = models.TextField()
    writer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    tags = models.ManyToManyField('tag.Tag')
    like = models.ManyToManyField('accounts.User', related_name='likes', blank=True)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'community_boards'
        verbose_name = '커뮤니티 게시판'
        verbose_name_plural = '커뮤니티 게시판'


class Comment(models.Model):
    comment = models.TextField()
    # 글 작성자
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    # 게시글
    post = models.ForeignKey('Board', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

    class Meta:
        db_table = 'community_comment'
        verbose_name = '댓글'
        verbose_name_plural = '댓글'