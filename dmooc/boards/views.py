from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Board, Comment
from .forms import BoardForm, CommentForm
from accounts.models import User
from tag.models import Tag
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from django.db.models import Q

# 글쓰기
def board_write(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login')

    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            user_id = request.user
            user = User.objects.get(pk=user_id)
            tags = form.cleaned_data['tags'].split(',')

            board = Board()
            board.title = form.cleaned_data['title']
            board.contents = form.cleaned_data['contents']
            board.writer = user
            board.save()

            for tag in tags:
                if not tag:
                    continue
                _tag, _ = Tag.objects.get_or_create(name=tag)
                board.tags.add(_tag)

            return redirect('/boards/list')
    else:
        form = BoardForm()
    return render(request, 'board_write.html', {'form': form})


# 클릭한 게시물 보기
def board_detail(request, pk):  # pk: url 작성 시 가져옴
    board = get_object_or_404(Board, pk=pk)
    comments = CommentForm()
    comment_view = Comment.objects.filter(post=pk)

    real_writer = True
    if board.writer == request.user:
        real_writer = True
    else:
        real_writer = False

    return render(request, 'board_detail.html', {'board': board, 'comments': comments,
                                                 'comment_view': comment_view, 'writer': real_writer})


# 모든 게시물 보기
def board_list(request):
    all_boards = Board.objects.all().annotate(
        num_comment=Count('comment')).order_by('like_count')
    page = int(request.GET.get('p', 1))
    paginator = Paginator(all_boards, 5)
    boards = paginator.get_page(page)

    return render(request, 'board_list.html', {'boards': boards})

# 게시글 삭제
def board_delete(request, pk):
    user_id = request.user
    board = get_object_or_404(Board, id=pk)
    if board.writer == user_id:
        board.delete()
        return redirect('/boards/list/')
    else:
        return redirect('/detail/{pk}/')


def comment_write(request, board_id):
    comment_write = CommentForm(request.POST)
    user_id = request.user
    user = User.objects.get(pk=user_id)
    if comment_write.is_valid():
        comments = comment_write.save(commit=False)
        comments.post = get_object_or_404(Board, pk=board_id)
        comments.author = user
        comments.save()

    return redirect('board_detail', board_id)


def likes(request, board_id):
    like_b = get_object_or_404(Board, id=board_id)
    if request.user in like_b.like.all():
        like_b.like.remove(request.user)
        like_b.like_count -= 1
        like_b.save()
    else:
        like_b.like.add(request.user)
        like_b.like_count += 1
        like_b.save()
    return redirect('board_detail', board_id)

############################################################
# 게시글 검색
def get_queryset(self):
    search_keyword = self.request.GET.get('q', '')
    search_type = self.request.GET.get('type', '')
    notice_list = Board.objects.order_by('-id')

    if search_keyword :
        if len(search_keyword) > 1 :
            if search_type == 'all':
                search_notice_list = notice_list.filter(Q (title__icontains=search_keyword) | Q (content__icontains=search_keyword) | Q (writer__user_id__icontains=search_keyword))
            elif search_type == 'title_content':
                search_notice_list = notice_list.filter(Q (title__icontains=search_keyword) | Q (content__icontains=search_keyword))
            elif search_type == 'title':
                search_notice_list = notice_list.filter(title__icontains=search_keyword)
            elif search_type == 'content':
                search_notice_list = notice_list.filter(content__icontains=search_keyword)
            elif search_type == 'writer':
                search_notice_list = notice_list.filter(writer__user_id__icontains=search_keyword)

            return search_notice_list
        else:
            messages.error(self.request, '검색어는 2글자 이상 입력해주세요.')
    return notice_list

def get_context_data(self, **kwargs):
    search_keyword = self.request.GET.get('q', '')
    search_type = self.request.GET.get('type', '')

    context = {}
    if len(search_keyword) > 1:
        context['q'] = search_keyword
    context['type'] = search_type

    return context