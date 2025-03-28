from django.db import models
from urllib.parse import urlparse, parse_qs

class TutorialCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Tutorial(models.Model):
    category = models.ForeignKey(TutorialCategory, on_delete=models.CASCADE, related_name='tutorials',null=True)
    title = models.CharField(max_length=200,null=True)
    description = models.TextField(null=True)
    video_url = models.URLField(null=True)

    def __str__(self):
        return self.title

    def save(self):
        self.video_url = self.embed_url
        return super().save()
    
    @property
    def embed_url(self):
        parsed_url = urlparse(self.video_url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            query = parse_qs(parsed_url.query)
            video_id = query.get('v')
            if video_id:
                return f"https://www.youtube.com/embed/{video_id[0]}"
        elif parsed_url.hostname == 'youtu.be':
            return f"https://www.youtube.com/embed{parsed_url.path}"
        return self.video_url
