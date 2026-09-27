# Create your views here.
# chat/views.py
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from asgiref.sync import async_to_sync
import channels.layers
from datetime import timedelta
from django.utils import timezone

from .helpers import check_participation, clean_unused_rooms, generate_cells
from .models import User, Board, Cell, Board_Participation, Room


def index(request):
    clean_unused_rooms()
    rooms = Room.objects.all()
    paginator = Paginator(rooms, 10) # 10 posts per page
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number) # retrieve page 1

    return render(request, "final/index.html", {
        'page': page
    })

# create room
@login_required
def create_room(request):
    # check for existing participation (active/spectator)
    participation = check_participation(request.user)
    # create room_id here using room_name, assign it to the websocket on the js file later
    if not participation:
        try:
            room = Room.objects.create()
            board = Board.objects.create(room=room)
            # generate cells for newly created board
            generate_cells(board)
            Board_Participation.objects.create(user=request.user,last_seen=timezone.now(), board=board,has_left=False,status='active').save()
            return HttpResponseRedirect(reverse('room', args=[room.id]))
        except IntegrityError:
            return HttpResponse('Unable to Create Room.')
    else:
        return render(request, "final/confirmation.html", {  
                'active_room': participation.board.room.id,
                'role': participation.status,
                'url': 'create_room'
        })    
@login_required 
def room(request, room_id):
    # retrieve desired room and current board
    try:
        room = Room.objects.get(pk=room_id)
        board = Board.objects.get(room=room, is_finished=False)
    except ObjectDoesNotExist:
        # if room has been deleted
        return HttpResponseRedirect(reverse('index'))
    
    participation = check_participation(request.user)
    if participation:
        if participation.board.room != room: 
            return render(request, "final/confirmation.html", {  
                    'active_room': participation.board.room.id,
                    'role': participation.status,
                    'url': 'join_room',
                    'room_id': room_id
            })    
    
    # assess if rejoiners are allowed
    try:
        current_participation = Board_Participation.objects.get(user=request.user, board=board)
        # implement new game design
        if current_participation.has_left:
            current_participation.has_left = False
        current_participation.last_seen = timezone.now()
        current_participation.save()
         # update player list to previous group
        channel_layer = channels.layers.get_channel_layer()
        # notifies previous room that user has left
        async_to_sync(channel_layer.group_send)( 
            f"room_{current_participation.board.room.id}",
            {
                "type": "player.render", "participants": current_participation.board.serialize_participants()
            }
        )
        
    except ObjectDoesNotExist:
        # new players
            try:
                if board.is_generated:
                    new_participation = Board_Participation.objects.create(user=request.user,last_seen=timezone.now(), board=board,has_left=False,status='spectator')
                else:
                    new_participation = Board_Participation.objects.create(user=request.user,last_seen=timezone.now(), board=board,has_left=False,status='active')
                new_participation.save()
                # update player list to previous group
                channel_layer = channels.layers.get_channel_layer()
                # notifies previous room that user has left
                async_to_sync(channel_layer.group_send)(
                    f"room_{new_participation.board.room.id}",
                    {
                        "type": "player.render", "participants": new_participation.board.serialize_participants()
                    }
                )
            except IntegrityError:
                return HttpResponse('Joining Room Error')
        
    # finally render room
    return render(request, "final/room.html", {
        "room_id": room.id,
        "board_id": board.id
    })

@login_required 
def confirm_room(request):
    if request.method == 'POST':
        # clean old participations
        participation = check_participation(request.user)
        if participation:
            participation.has_left = True
            participation.save()

        # update player list to previous group
        channel_layer = channels.layers.get_channel_layer()
        # notifies previous room that user has left
        async_to_sync(channel_layer.group_send)(
            f"room_{participation.board.room.id}",
            {
                "type": "player.render", "participants": participation.board.serialize_participants()
            }
        )

        # decide whether to create/join
        url = request.POST['source']
        if url == 'join_room':
            room_id = request.POST['room_id']
            return HttpResponseRedirect(reverse('room', args=[room_id]))
        else:
            return HttpResponseRedirect(reverse('create_room'))

@login_required 
def leave_room(request):
    participation = check_participation(request.user)
    if participation:
        participation.has_left = True
        participation.save()
        # update player list to previous group
        channel_layer = channels.layers.get_channel_layer()
        # notifies previous room that user has left
        async_to_sync(channel_layer.group_send)(
            f"room_{participation.board.room.id}",
            {
                "type": "player.render", "participants": participation.board.serialize_participants()
            }
        )
    return HttpResponseRedirect(reverse('index'))
        
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
  
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "final/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "final/login.html")

def logout_view(request):
    # force to end websocket connection if one exist
    participation = check_participation(request.user)
    if participation:
        participation.has_left = True
        participation.save()
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "final/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "final/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "final/register.html")