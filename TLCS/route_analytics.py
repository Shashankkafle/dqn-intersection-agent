import sumolib

# class RouteAnalytics:
#     def __init__(self):
#         pass
    
def get_analysis_flow(route_file,max_steps,car_count):
        # Load the route file
        vehicles = list(sumolib.output.parse(route_file, "vehicle"))
        j=0
        i=0
        V_15 = 0
        while j< len(vehicles):
            # print("loop start i,j",i,j)
            i_depart = float(vehicles[i].depart)
            j_depart = float(vehicles[j].depart)
            # print("i,j, i_depart-j_depart)/60,V_15",i,j,(i_depart-j_depart)/60,V_15)

            # if((vehicles[j]-vehicles[i]) <= 5 ):
            if((j_depart - i_depart)/60 <= 15 ):
                j = j+1
            else:
                if(V_15<j-i):
                    V_15 = j-i
                i=j
        V = car_count/(max_steps/3600)    
        analysis_flow_rate = V/(4*V_15)
        print("analysis_flow_rate,V,V_15",analysis_flow_rate)
        return analysis_flow_rate





