import django_filters
from .models import Video

class VideoFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Video
        fields = ['title']
