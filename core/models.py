from django.db import models

class FederalConstituency(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # e.g., HOR-74-1
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ElectionResult(models.Model):
    ELECTION_TYPE_CHOICES = [
        ('federal', 'Federal'),
        ('provincial', 'Provincial'),
        ('local', 'Local'),
    ]

    election_type = models.CharField(max_length=20, choices=ELECTION_TYPE_CHOICES)
    constituency = models.ForeignKey(FederalConstituency, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=100)
    party = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100, blank=True, null=True)
    votes = models.IntegerField()
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    year = models.IntegerField()
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.candidate_name} ({self.party}) - {self.constituency} [{self.election_type}]"
