from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from ..models import Review
from ..forms import ReviewForm


@login_required(redirect_field_name='user_login/')
def create_review(request):
    """View for creating or updating a review (max one per user)"""
    # Check if user already has a review
    existing_review = None
    try:
        existing_review = Review.objects.get(user=request.user)
    except Review.DoesNotExist:
        pass
    
    if request.method == 'POST':
        if existing_review:
            # Update existing review
            form = ReviewForm(request.POST, instance=existing_review)
            action = "ažurirali"
        else:
            # Create new review
            form = ReviewForm(request.POST)
            action = "dodali"
            
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, f'Uspešno ste {action} svoju recenziju!')
            return redirect('reviews_list')
    else:
        # Display form (new or pre-filled for existing review)
        form = ReviewForm(instance=existing_review if existing_review else None)
    
    context = {
        'form': form,
        'existing_review': existing_review,
        'is_update': existing_review is not None
    }
    return render(request, 'appointment/reviews/create_review.html', context)


def reviews_list(request):
    """Public view showing all approved reviews"""
    reviews = Review.objects.filter(is_approved=True).select_related('user')
    
    # Calculate average rating and total count
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Round average rating to 1 decimal place
    if stats['average_rating']:
        stats['average_rating'] = round(stats['average_rating'], 1)
    else:
        stats['average_rating'] = 0
    
    # Calculate star distribution with percentages for display
    star_distribution = {}
    total_reviews = stats['total_reviews']
    for i in range(1, 6):
        count = reviews.filter(rating=i).count()
        percentage = round((count * 100 / total_reviews), 1) if total_reviews > 0 else 0
        star_distribution[i] = {
            'count': count,
            'percentage': percentage
        }
    
    context = {
        'reviews': reviews,
        'stats': stats,
        'star_distribution': star_distribution
    }
    return render(request, 'appointment/reviews/reviews_list.html', context)


@login_required(redirect_field_name='user_login/')
def delete_review(request, review_id):
    """Allow user to delete their own review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Vaša recenzija je uspešno obrisana.')
        return redirect('reviews_list')
    
    context = {'review': review}
    return render(request, 'appointment/reviews/delete_review.html', context)