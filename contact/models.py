from django.db import models


CATEGORY_CHOICES = (
    ("general", "General Enquiry"),
    ("booking", "Booking Query"),
    ("complaint", "Complaint"),
    ("feedback", "Feedback"),
)


class ContactRequest(models.Model):
    """
    Stores a single contact form submission.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.category} from {self.name}"