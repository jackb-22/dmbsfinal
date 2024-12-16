from django.test import TestCase
from .models import Building, Room, CommunityDirector, Student, Leases
from datetime import date, timedelta
from django.db import IntegrityError

class HousingSystemTests(TestCase):
    def setUp(self):
        # Create initial data
        self.building = Building.objects.create(building_code='CRO', num_rooms=5)
        self.cd = CommunityDirector.objects.create(pidm=101, name='John Smith')
        self.room = Room.objects.create(
            room_num=1,
            building_code=self.building,
            num_beds=2,
            cd=self.cd,
            status='open',
            deletable=True
        )
        self.student1 = Student.objects.create(pidm=201, name='Alice Doe', stud_ID=1001)
        self.student2 = Student.objects.create(pidm=202, name='Bob Smith', stud_ID=1002)

    def test_valid_building_and_room_creation(self):
        """Test that buildings and rooms can be created with valid constraints."""
        self.assertEqual(Building.objects.count(), 1)
        self.assertEqual(Room.objects.count(), 1)

    def test_invalid_room_bed_count(self):
        """Test that rooms cannot have invalid bed counts."""
        with self.assertRaises(IntegrityError):
            Room.objects.create(
                room_num=2,
                building_code=self.building,
                num_beds=6,  # Invalid bed count
                cd=self.cd
            )

    def test_valid_lease_dates(self):
        """Test that leases respect the date constraints."""
        lease = Leases.objects.create(
            pidm=self.student1,
            room_num=self.room.room_num,
            building_code=self.building,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        self.assertIsNotNone(lease)

    def test_invalid_lease_dates(self):
        """Test that leases with invalid dates raise errors."""
        with self.assertRaises(IntegrityError):
            Leases.objects.create(
                pidm=self.student1,
                room_num=self.room.room_num,
                building_code=self.building,
                start_date=date.today() + timedelta(days=30),
                end_date=date.today()
            )

    def test_trigger_update_room_status(self):
        """Test that room status updates to 'closed' when full and 'open' otherwise."""
        # Add two leases to fill the room
        Leases.objects.create(
            pidm=self.student1,
            room_num=self.room.room_num,
            building_code=self.building,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        Leases.objects.create(
            pidm=self.student2,
            room_num=self.room.room_num,
            building_code=self.building,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        # Reload room and check status
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'closed')

    def test_trigger_reopen_room_status(self):
        """Test that room status reopens when a lease is removed."""
        lease = Leases.objects.create(
            pidm=self.student1,
            room_num=self.room.room_num,
            building_code=self.building,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        # Check status after lease
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'open')

        # Remove lease
        lease.delete()
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'open')

    def test_no_delete_non_deletable_room(self):
        """Test that non-deletable rooms cannot be deleted."""
        self.room.deletable = False
        self.room.save()
        
        with self.assertRaises(IntegrityError):
            self.room.delete()

    def test_no_delete_building_with_rooms(self):
        """Test that buildings with rooms cannot be deleted."""
        with self.assertRaises(IntegrityError):
            self.building.delete()
