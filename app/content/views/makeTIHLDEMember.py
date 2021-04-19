from app.common.permissions import IsDev, IsHS                                  
from rest_framework.decorators import api_view, permission_classes              
from rest_framework.response import Response                                    
from rest_framework import status                                               
from app.group.models import Group, Membership                                  
from app.common.enums import Groups                                             
from app.content.models import User                                             
                                                                                                                                            
                                                                                 
                                                                                 
@api_view(["POST"])                                                             
@permission_classes([IsDev, IsHS])                                              
def makeTIHLDEMember(request):                                                                                                                      
    # serializer = MakeUserSerializer(data=request.data)                        
    # if not serializer.is_valid():                                             
    #     return Response(                                                      
    #         {"detail": "Ugyldig brukernavn"}, status=status.HTTP_400_BAD_REQUEST
    #     )                                                                     
                                                                                
    TIHLDE = Group.objects.get(slug=Groups.TIHLDE)                              
    user_id = request.data["user_id"]                                           
    user = User.objects.get(user_id=user_id)                                    
    if user is not None:                                                        
                                                                                
        Membership.objects.get_or_create(user=user, group=TIHLDE)               
        return Response(                                                        
            {"detail": "Brukeren ble lagt til som TIHLDE medlem"},              
            status=status.HTTP_200_OK,                                          
        )                                                                       
    else:                                                                       
        return Response(                                                        
            {"detail": "Ugyldig brukernavn"}, status=status.HTTP_400_BAD_REQUEST
        )
