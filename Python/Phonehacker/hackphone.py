import phonenumbers
from phonenumbers import geocoder
phone_number1 = phonenumbers.parse("+250781202570")
phone_number2 = phonenumbers.parse("+201234567890")
phone_number3 = phonenumbers.parse("+12136574429")
phone_number4 = phonenumbers.parse("+917294536271")

print("\nPhone Numbers Location\n")
print(geocoder.description_for_number(phone_number1, "en"));
print(geocoder.description_for_number(phone_number2, "en"));
print(geocoder.description_for_number(phone_number3, "en"));
print(geocoder.description_for_number(phone_number4, "en"));