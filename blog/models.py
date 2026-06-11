# blog/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _
import nepali_datetime  # Import the B.S. calendar converter

class Article(models.Model):
    # ... (Keep your existing title, content, and image fields exactly the same) ...
    
    title_ne = models.CharField(_("Title (Nepali)"), max_length=255)
    title_en = models.CharField(_("Title (English)"), max_length=255)
    content_ne = models.TextField(_("Content (Nepali)"))
    content_en = models.TextField(_("Content (English)"))
    featured_image_url = models.URLField(_("Featured Image URL"), max_length=500, blank=True, null=True)
    featured_image_file = models.ImageField(_("Upload Photo from Device"), upload_to='blog_photos/', blank=True, null=True)
    
    published_date = models.DateTimeField(_("Published Date"), default=timezone.now)
    is_alert = models.BooleanField(_("Is Critical Emergency Alert?"), default=False)

    class Meta:
        ordering = ['-published_date']
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

    @property
    def title(self):
        return self.title_ne if get_language() == 'ne' else self.title_en

    @property
    def content(self):
        return self.content_ne if get_language() == 'ne' else self.content_en

    @property
    def image_url(self):
        """
        Safely extracts the Cloudinary URL string by verifying actual file properties.
        Falls back to raw text URLs or a default static placeholder asset.
        """
        # 1. Check Cloudinary file storage safely
        if self.featured_image_file and hasattr(self.featured_image_file, 'url'):
            try:
                # FIXED: Define the variable FIRST, then print/inspect it!
                url_str = self.featured_image_file.url
                
                if url_str and "None" not in str(url_str) and url_str.strip() != "":
                    return url_str
            except Exception as e:
                # Optional: print the actual error to your terminal console for transparency
                print(f"Cloudinary extraction exception caught: {e}")
                pass

        # 2. Dropback fallback: Manually inputted text URL string
        if self.featured_image_url and self.featured_image_url.strip():
            return self.featured_image_url.strip()

        # 3. Last resort fallback: Local default image asset block
        return "https://images.unsplash.com/photo-1450133064473-71024230f91b?q=80&w=600" # A premium, neutral placeholder link

    # --- NEW SMART DATE PROPERTY ---
    @property
    def formatted_date(self):
        """
        Returns a beautifully localized Bikram Sambat date string for Nepali users,
        and a standard formatted Gregorian date string for English users.
        """
        if get_language() == 'ne':
            # Convert the Gregorian UTC/Local timestamp to Nepali Bikram Sambat
            nepali_date = nepali_datetime.date.from_datetime_date(self.published_date.date())
            
            # Format pattern: %K=Year, %N=Month Name, %D=Day in Devnagari
            # This generates exactly: "२०८३ जेठ २७ गते"
            return nepali_date.strftime('%K %N %D गते')
        
        # Fallback for English: "June 10, 2026"
        return self.published_date.strftime('%B %d, %Y')

    def __str__(self):
        return self.title_en