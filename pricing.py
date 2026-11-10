from datetime import datetime,timedelta
class Pricing:
    
    def calculate_room_charges(self,room_type,base_rate,check_in,check_out,no_of_guests,completed_stays,break_fast="no"):
        check_in=datetime.strptime(check_in,"%Y-%m-%d").date()
        check_out=datetime.strptime(check_out,"%Y-%m-%d").date()
        nights=(check_out-check_in).days
        if nights<=0:
            raise ValueError("Check-out date must be after check-in date")
        total_room_charge=0
        gst_amount=0
        current_date=check_in
        nightly_breakdown=[]
        
        while current_date<check_out:
            daily_rate=base_rate
            if current_date.weekday() in (4,5):
                daily_rate+=daily_rate*0.2
            total_room_charge+=daily_rate
            nightly_breakdown.append({
                "date":current_date.strftime("%d-%m-%Y"),
                "charge":round(daily_rate,2)
            })
            if daily_rate<=7500:
                gst_amount+=daily_rate*0.12
            else:
                gst_amount+=daily_rate*0.18
            current_date=current_date+timedelta(days=1)
        extra_guest_charge=0
        if room_type in ("Deluxe","Suite") and no_of_guests>2:
            extra_guest=no_of_guests-2
            extra_guest_charge=extra_guest*800*nights
        
        breakfast_charge=0
        if break_fast=="yes":
            breakfast_charge=350*no_of_guests*nights
        room_charges=total_room_charge+extra_guest_charge+breakfast_charge
        # gst_amount=room_reve
        long_stay_discount=0
        loyalty_discount=0
        if nights>=7:
            long_stay_discount=room_charges*0.10
        if completed_stays>=3:
            loyalty_discount=room_charges*0.05
        total_discount=long_stay_discount+loyalty_discount
        discounted_room_charge=room_charges-total_discount

        if room_charges>0:
            gst_amount=gst_amount*(discounted_room_charge/room_charges)
        final_amount=discounted_room_charge+gst_amount
        room_revenue=discounted_room_charge
        return {
            "no_of_nights":nights,
            "nightly_breakdown":nightly_breakdown,
            "room_charge":total_room_charge,
            "extra_guest_charge":extra_guest_charge,
            "breakfast_charge":breakfast_charge,
            "total_room_charge":room_charges,
            "long_stay_discount":long_stay_discount,
            "loyalty_discount":loyalty_discount,
            "total_discount":total_discount,
            "discounted_room_charge":discounted_room_charge,
            # "gst_rate":gst_rate*100,
            "room_revenue":room_revenue,
            "gst_amount":gst_amount,
            "final_amount":final_amount
        }

# pricing=Pricing()
# result=pricing.calculate_room_charges("Deluxe",5000,"6-11-2026","9-11-2026",4)
# print(result)