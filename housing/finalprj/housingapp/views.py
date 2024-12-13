from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Building, Room, Student, CommunityDirector
from .forms import BuildingForm, RoomForm, StudentForm, CDForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Building, Room, Student, CommunityDirector, Lease
from .forms import BuildingForm, RoomForm, StudentForm, CDForm, LeaseForm


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        print(f"Entered username: {username}, Entered password: {password}")

        if username == "admin" and password == "12345":
            print("Admin login successful")
            request.session['user_type'] = 'admin'
            return redirect('admin_dashboard')

        try:
            cd = CommunityDirector.objects.get(name=username)
            if cd and cd.pidm == int(password):  
                print(f"{username} login successful")
                request.session['user_type'] = 'cd'
                request.session['cd_name'] = username  
                return redirect('cd_dashboard')
        except CommunityDirector.DoesNotExist:
            pass  

        print("Invalid username or password")
        messages.error(request, "Invalid username or password.")
        return render(request, 'housingapp/login.html')

    return render(request, 'housingapp/login.html')
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CommunityDirector, Lease, Room, Student

def cd_dashboard(request):

    if request.session.get('user_type') != 'cd':
        return redirect('login')  
    cd_name = request.session.get('cd_name')

    try:
        cd = CommunityDirector.objects.get(name=cd_name)
        
        building_code = cd.building_code
        

        rooms = Room.objects.filter(building_code=building_code, status='open')  

        leases = Lease.objects.filter(room_num__building_code=building_code)


        students_with_leases = [
            {
                'student': lease.stud_ID,
                'room_num': lease.room_num.room_num 
            }
            for lease in leases
        ]

        context = {
            'cd_name': cd_name,
            'building_code': building_code.building_code,
            'rooms': rooms,
            'students_with_leases': students_with_leases,
            'current_year': 2024  
        }
        return render(request, 'housingapp/cd_dashboard.html', context)
    except CommunityDirector.DoesNotExist:
        return redirect('login')
    
    except CommunityDirector.DoesNotExist:
        messages.error(request, "Community Director not found.")
        return redirect('login')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def admin_dashboard(request):
    if request.session.get('user_type') != 'admin':
        return redirect('login')

    buildings = Building.objects.all()
    rooms = Room.objects.all()
    students = Student.objects.all()
    cds = CommunityDirector.objects.all()
    leases = Lease.objects.all()

    if request.method == "POST":
        try:
            if 'add_building' in request.POST:
                form_building = BuildingForm(request.POST)
                if form_building.is_valid():
                    form_building.save()
                    messages.success(request, "Building added successfully!")
                else:
                    for field, errors in form_building.errors.items():
                        messages.error(request, f"Error in {field}: {', '.join(errors)}")

            elif 'add_room' in request.POST:
                form_room = RoomForm(request.POST)
                if form_room.is_valid():
                    room = form_room.save(commit=False)

                    building = Building.objects.get(building_code=room.building_code.building_code)
                    if room.room_num > building.num_rooms:
                        raise ValidationError(f"Room number {room.room_num} exceeds building capacity of {building.num_rooms}.")

                    room.save()
                    messages.success(request, "Room added successfully!")
                else:
                    for field, errors in form_room.errors.items():
                        messages.error(request, f"Error in {field}: {', '.join(errors)}")

            elif 'add_student' in request.POST:
                form_student = StudentForm(request.POST)
                if form_student.is_valid():
                    form_student.save()
                    messages.success(request, "Student added successfully!")
                else:
                    for field, errors in form_student.errors.items():
                        messages.error(request, f"Error in {field}: {', '.join(errors)}")

            elif 'add_cd' in request.POST:
                form_cd = CDForm(request.POST)
                if form_cd.is_valid():
                    form_cd.save()
                    messages.success(request, "Community Director added successfully!")
                else:
                    for field, errors in form_cd.errors.items():
                        messages.error(request, f"Error in {field}: {', '.join(errors)}")

            elif 'add_lease' in request.POST:
                form_lease = LeaseForm(request.POST)
                if form_lease.is_valid():
                    lease = form_lease.save(commit=False)

                    room = lease.room_num
                    num_active_leases = Lease.objects.filter(room_num=room, end_date__gte=request.POST['start_date']).count()
                    if num_active_leases >= room.num_beds:
                        raise ValidationError(f"Room {room} has reached its capacity of {room.num_beds} beds.")
                    
                    lease.save()
                    messages.success(request, "Lease added successfully!")
                else:
                    for field, errors in form_lease.errors.items():
                        messages.error(request, f"Error in {field}: {', '.join(errors)}")

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, 'housingapp/admin_dashboard.html', {
        'buildings': buildings,
        'rooms': rooms,
        'students': students,
        'cds': cds,
        'leases': leases,
    })


def delete_building(request, building_code):
    building = get_object_or_404(Building, building_code=building_code)
    try:
        building.delete()
        messages.success(request, "Building deleted successfully.")
    except ValidationError as e:
        messages.error(request, e.message)
    return redirect('admin_dashboard')

def delete_cd(request, pidm):
    cd = get_object_or_404(CommunityDirector, pidm=pidm)
    try:
        cd.delete()
        messages.success(request, f"Community Director {cd.name} deleted successfully.")
    except ValidationError as e:
        messages.error(request, e.message)
    return redirect('admin_dashboard')

def delete_room(request, room_num, building_code):
    room = get_object_or_404(Room, room_num=room_num, building_code=building_code)
    if room.deletable:
        room.delete()
        messages.success(request, f"Room {room.room_num} deleted successfully.")
    else:
        messages.error(request, f"Room {room.room_num} cannot be deleted.")
    return redirect('admin_dashboard')

def delete_lease(request, stud_ID, room_num):
    lease = get_object_or_404(Lease, stud_ID_id=stud_ID, room_num_id=room_num)
    try:
        lease.delete()
        messages.success(request, "Lease deleted successfully.")
    except ValidationError as e:
        messages.error(request, e.message)
    return redirect('admin_dashboard')

def delete_student(request, stud_ID):
    student = get_object_or_404(Student, stud_ID=stud_ID)
    try:
        student.delete()
        messages.success(request, f"Student {stud_ID} deleted successfully.")
    except ValidationError as e:
        messages.error(request, e.message)
    return redirect('admin_dashboard')