from rest_framework import serializers

class StudentSerializer(serializers.Serializer):
    id = serializers.CharField()  
    name = serializers.CharField(max_length=100)  
    age = serializers.IntegerField()  
    email = serializers.EmailField()  