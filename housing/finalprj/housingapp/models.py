from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Building(models.Model):
    building_code = models.CharField(
        max_length=3, 
        primary_key=True, 
    )
    num_rooms = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])

    def __str__(self):
        return self.building_code


class CommunityDirector(models.Model):
    pidm = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    building_code = models.ForeignKey(Building, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Room(models.Model):
    room_num = models.IntegerField(primary_key=True)
    building_code = models.ForeignKey(Building, on_delete=models.CASCADE)
    num_beds = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    cd = models.ForeignKey(CommunityDirector, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        default='open', 
        choices=[('open', 'open'), ('closed', 'closed'), ('unrentable', 'unrentable')]
    )
    deletable = models.BooleanField(default=False)

    class Meta:
        unique_together = ('room_num', 'building_code')

    def __str__(self):
        return f"{self.building_code.building_code}-{self.room_num}"

    def save(self, *args, **kwargs):
        if self.room_num > self.building_code.num_rooms:
            raise ValidationError(f"Room number {self.room_num} exceeds building capacity of {self.building_code.num_rooms}.")
        super().save(*args, **kwargs)


class Student(models.Model):
    stud_ID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Lease(models.Model):
    stud_ID = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    room_num = models.ForeignKey(Room, on_delete=models.CASCADE, default=0)

    class Meta:
        unique_together = ('stud_ID', 'room_num')

    def __str__(self):
        return f"Lease for {self.stud_ID}"

@receiver(pre_delete, sender=Building)
def prevent_building_deletion_with_rooms(sender, instance, **kwargs):
    if Room.objects.filter(building_code=instance).exists():
        raise ValidationError("Cannot delete a building that has rooms.")

@receiver(post_save, sender=Lease)
def update_room_status_on_lease(sender, instance, created, **kwargs):
    if created:
        room = instance.room_num
        leases_in_room = Lease.objects.filter(room_num=room).count()
        if leases_in_room >= room.num_beds:
            room.status = 'closed'
            room.save()

@receiver(post_save, sender=Lease)
def reopen_room_on_lease_end(sender, instance, **kwargs):
    room = instance.room_num
    if Lease.objects.filter(room_num=room, end_date__gte=instance.end_date).count() == 0:
        room.status = 'open'
        room.save()

@receiver(pre_delete, sender=Student)
def prevent_student_deletion_with_active_lease(sender, instance, **kwargs):
    if Lease.objects.filter(stud_ID=instance).exists():
        raise ValidationError("Cannot delete a student with active leases.")


