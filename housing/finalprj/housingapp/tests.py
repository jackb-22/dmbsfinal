from django.test import TestCase
from .models import Building, Room, CommunityDirector, Student, Campus_Students, Leases
from django.db.utils import IntegrityError
from datetime import date

class HousingSystemTests(TestCase):
    def setUp(self):
        # Create initial Building, Community Director, Room, and Student objects for tests
        self.building = Building.objects.create(building_code=1, num_avail_rooms=10)
        self.cd = CommunityDirector.objects.create(pidm=201, name="John", last_name="Smith")
        self.room = Room.objects.create(room_num=101, building_code=self.building, num_beds=2)
        self.student = Student.objects.create(stud_ID=1001, name="Alice", last_name="Doe")
        self.campus_student = Campus_Students.objects.create(stud_ID=self.student.stud_ID)

    def test_invalid_bed_count(self):
        """Test adding a room with an invalid number of beds (outside 1-5 range)."""
        with self.assertRaises(IntegrityError):
            Room.objects.create(room_num=102, building_code=self.building, num_beds=6)

    def test_exceed_room_capacity(self):
        """Test assigning more students to a room than its capacity allows."""
        # First lease
        Leases.objects.create(
            stud_ID=self.campus_student,
            room_num=self.room,
            building_code=self.building,
            start_date=date(2024, 9, 1),
            end_date=date(2025, 5, 31)
        )
        # Second lease
        Leases.objects.create(
            stud_ID=Campus_Students.objects.create(stud_ID=1002),
            room_num=self.room,
            building_code=self.building,
            start_date=date(2024, 9, 1),
            end_date=date(2025, 5, 31)
        )
        # Third lease should fail as room capacity is 2
        with self.assertRaises(IntegrityError):
            Leases.objects.create(
                stud_ID=Campus_Students.objects.create(stud_ID=1003),
                room_num=self.room,
                building_code=self.building,
                start_date=date(2024, 9, 1),
                end_date=date(2025, 5, 31)
            )

    def test_cascade_delete_building(self):
        """Test that deleting a building cascades deletes for its rooms."""
        self.assertEqual(Room.objects.count(), 1)
        self.building.delete()
        self.assertEqual(Room.objects.count(), 0)

    def test_lease_date_validation(self):
        """Test lease creation with invalid start and end dates."""
        with self.assertRaises(IntegrityError):
            Leases.objects.create(
                stud_ID=self.campus_student,
                room_num=self.room,
                building_code=self.building,
                start_date=date(2025, 6, 1),  # Invalid: end date earlier than start
                end_date=date(2025, 5, 31)
            )

    def test_delete_student_with_leases(self):
        """Test preventing deletion of a student with active leases."""
        Leases.objects.create(
            stud_ID=self.campus_student,
            room_num=self.room,
            building_code=self.building,
            start_date=date(2024, 9, 1),
            end_date=date(2025, 5, 31)
        )
        with self.assertRaises(IntegrityError):
            self.student.delete()
