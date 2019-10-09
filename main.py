import sys
import pprint
import math
import time
import math
import matplotlib.path as mpltPath
from numpy import arange,array,ones
from scipy import stats
from base.base_uav import BaseUAV

class KAGUAV(BaseUAV):
    def initialize(self):
        self.gps = [[0,0,0,0],[0,0,0,0]]#bos gps verisi
        self.formation_really_end=False#formasyon gercekten bitti
        self.uav_fuel_error=False#benzin ikaz isigi
        self.speed_15_gidilen_yol=40#40 la giderken litre basina yol
        self.speed_60_gidilen_yol=175#60 la giderken litre basina yol
        self.denied_varis=[0,0]#denied varis noktasi
        self.denied_varis_bulundu=True#daha once varis noktasi bulundu mu
        self.formation_end=True#formasyonun bittigini soyler
        self.game_saved=True#baslangic konumu kayit sinyali
        self.starting_location=[0,0]#baslangic konumlarinin lokasyonlari
        self.arrow=False#formsyon ok sinyali
        self.square=False#formasyon prism sinyali
        self.first_move=True
        self.starting_altitude=0#baslangic yuksekligi
        self._uav_id=int(self.uav_id)#id mizin int degeri
        self.searchId=self._uav_id
        self.uav_height=9 #yukselme miktari
        self.uav_collision_slow_rate=1 #carpisma ani yavaslama orani
        self.default_altitude = 100 #klasik sukseklik
        self.formation_distance_tolerance = 5 #formasyon konumu mesafe toleransi
        self.uav_front=10 #uav merkez kafa mesafesi
        self.range_rate=0.8 #dinamik carpisma capi yuzdesi
        self.tall_buildings=[]#uzun binalar
        self.yaraliKurtarma=0
        self.hastaneMesafe=9999
        self.hastaneX=0
        self.hastaneY=0
        self.center_of_world=[]
        self.count = 0
        self.defterx=[]
        self.deftery=[]




    def act(self):


        #self.yaraliX=218
        #self.yaraliY=78
        #self.yaraliKurtarma=1



        params=self.params
        data=self.uav_msg
        print("yakit",self.uav_fuel_error)
        print("noise",data["uav_guide"]["gps_noise_flag"])
        self.noise_filter(data)
        self.heading = data["active_uav"]["heading"]
        print("slm",self.center_of_world)


        if self.game_saved:
            self.center_of_world=self.merkeziBul(params)
            self.tall_buildings=self.tall_building(params)
            self.starting_location=data["active_uav"]["location"]
            self.starting_altitude=data["active_uav"]["altitude"]
            self.searchAltitude=params["logical_camera_height_max"]-1
            self.aralikBelirle(data,params)
            print(params)
            self.game_saved=False
            #benzinnnnnn bittiiiiiiiiiiiiiiiiiiiiiii knkkkkkkkkkk
        if self.yaraliKurtarma == 10:
            self.send_move_cmd(0,0,80,80)



        if self.uav_fuel_error:
            self.fallback(data,params)
                #print(data["active_uav"]["fuel_reserve"])
                #benzinnnnnnnnnnnn varrrrrrrrrrrrrrrrr knkkkkkkkkkkk

        if self.uav_fuel_error==False:
            self.fallback(data,params)
            #print(data["uav_guide"]["gps_noise_flag"])
            #ikinci True kontrolu
            if data["uav_guide"]["dispatch"]==False and self.formation_really_end==False:
                self.formation_end=False
                        #formasyon ok basi isteniyor
            if data["uav_formation"]["type"]=="arrow" and self.formation_really_end==False :
                self.FormationFlyArrow(data)
                        #formaston prizma isteniyor
            if data["uav_formation"]["type"]=="prism" and self.formation_really_end==False :
                self.FormationFlySquare(data)

                        #ikinci True yandi mi

            if data["uav_guide"]["dispatch"] and self.formation_end==False:
                time.sleep(self._uav_id*5)
                print("formasyon gercekten bitti")
                self.formation_really_end=True
                self.deniedZoneDocMekaniks(data,params)
                if self.denied_varis_bulundu==False:
                    self.DeniedZoneDocMekaniksStart(data,params)
                    if self.mesafe(data,self.denied_varis[0],self.denied_varis[1])>3:
                        self.denied_varis_bulundu=True
                        self.denied_varis=[0,0]

                if self.yaraliKurtarma==0:
                    self.replika_search(data,params)
                elif self.yaraliKurtarma==1:
                    self.kurtar(data,params)
                elif self.yaraliKurtarma==2:
                    self.yukselme(data,params)
                elif self.yaraliKurtarma==3:
                    self.transfer(data,params)
                elif self.yaraliKurtarma==4:
                    self.yaraliBirak(data,params)




    def noise_filter(self,data):
        loc_y=data["active_uav"]["location"][1]
        loc_x=data["active_uav"]["location"][0]
        if len(self.defterx)<=12:
            self.defterx.append(loc_x)
            self.deftery.append(loc_y)
        if len(self.defterx)==12:
            self.defterx.pop(0)
            self.deftery.pop(0)
        if data["uav_guide"]["gps_noise_flag"] == True:

            inds = arange(0,11)
            slope, intercept, r_value, p_value, std_err = stats.linregress(inds,self.defterx)
            linex = slope*inds+intercept
            tahminX=linex[5]
            slope, intercept, r_value, p_value, std_err = stats.linregress(inds,self.deftery)
            liney = slope*inds+intercept
            tahminY=liney[5]
            print("tahmin",tahminX,tahminY)
            print("reel",loc_x,loc_y)
            return [tahminX,tahminY]

    def yaraliBirak(self,data,params):
        release = params["injured_release_height"]
        if data["active_uav"]["altitude"]>release:
            self.yurukulum(data,self.hastaneX,self.hastaneY,release-1)
        else:
            #sira algoritmasi
            time.sleep(params["injured_release_duration"])
            self.yaraliKurtarma=0
    def hastaneBul(self,data,params):
        print("hastanebul calisiyor")
        for i in range (len(params["special_assets"])):
             if params["special_assets"][i]["type"]== 'hospital':
                 hastaneX=params["special_assets"][i]["location"]["x"]
                 hastaneY=params["special_assets"][i]["location"]["y"]
                 if self.mesafe(data,hastaneX,hastaneY) < self.hastaneMesafe:
                     self.hastaneX=hastaneX
                     self.hastaneY=hastaneY
    def transfer(self,data,params):
        print("transfer calisiyor")
        self.hastaneBul(data,params)
        if self.yurukulum(data,self.hastaneX,self.hastaneY,60)==True:
            self.yaraliKurtarma=4
    def yukselme(self,data,params):
        print("yuksel calisiyor")
        closeAltitude =self.altitude_control(data)
        if closeAltitude==0:
            if not data["active_uav"]["altitude"]<60:
                self.yurukulum(data,self.yaraliX,self.yaraliY,70)
            else:
                self.yaraliKurtarma=3
        else:
            self.yurukulum(data,self.yaraliX,self.yaraliY,closeAltitude-12)
    def kurtar(self,data,params):
        if self.yurukulum(data,self.yaraliX,self.yaraliY,params["injured_pick_up_height"])==True:
            self.send_move_cmd(0,0,data["active_uav"]["altitude"],params["injured_pick_up_duration"])
            time.sleep(params["injured_pick_up_duration"])
            self.yaraliKurtarma=2
            self.count=self.count-1
            print("KUrtar calisiyor")
    def saglikliVarmi(self,data):
        for i in range (len(data["casualties_in_world"])):
            if data["casualties_in_world"][i]["status"]=="healty":
                self.saglikliX=data["casualties_in_world"][i]["pose"][0]
                self.saglikliY=data["casualties_in_world"][i]["pose"][1]
                self.yaraliKurtarma=10

    def telecomaBak(self,data,params):
        telecomSayi=data["active_uav"]["equipments"]["telecom_beacon"]["telecom_served_people_count"]
        if telecomSayi>10:
            telecomHeight=params["telecom_height_max"]
            self.send_move_cmd(0,0,50,telecomHeight)
        return None

    def yaraliVarmi(self,data):
        uzunluk = len(data["casualties_in_world"])
        if uzunluk>0:
            for i in range (len(data["casualties_in_world"])):
                print("yarali bulundu")
                if data["casualties_in_world"][i]["status"]=="injured":
                    if data["casualties_in_world"][i]["in_world"]==True:
                        self.yaraliX=data["casualties_in_world"][i]["pose"][0]
                        self.yaraliY=data["casualties_in_world"][i]["pose"][1]
                        if self.mesafe(data,self.yaraliX,self.yaraliY)<70:
                            self.yaraliKurtarma=1
                            #self.kurtar(data,yaraliX,yaraliY)


    def kilavuz_heading(self,data):
        heading=data["uav_guide"]["heading"]
        if self.guide_heading[0]==0:
            self.guide_heading[0]=heading
        else:
            self.guide_heading[1]=heading
        fark=self.guide_heading[0]-self.guide_heading[1]
        fark=math.fabs(fark)
        self.guide_heading[0]=self.guide_heading[1]
        if fark>3:
            self.arrow==True
            self.prism==True



    def replika_search(self,data,params):
        alti_ctrl=self.altitude_control(data)
        if alti_ctrl!=0:
            if alti_ctrl>self.searchAltitude and data["active_uav"]["altitude"]>alti_ctrl:
                self.searchAltitude=alti_ctrl+self.uav_height
            if alti_ctrl<self.searchAltitude and data["active_uav"]["altitude"]<alti_ctrl:
                self.searchAltitude=alti_ctrl-self.uav_height
        else:
            self.searchAltitude=params["logical_camera_height_max"]-1

        if self.count==0:
            print("---1. checkpointe gidiliyor.")
            self.x_positioncalc=(self.searchId * self.aramaAraligi)+self.center_of_world[0]
            self.y_positioncalc=self.center_of_world[1]
            print(self.x_positioncalc,self.y_positioncalc)
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=1
                time.sleep(1)
        if self.count==1:
            print("--- ---2. checkpointe gidiliyor.")
            self.x_positioncalc=(self.searchId * self.aramaAraligi)+self.center_of_world[0]
            self.y_positioncalc=(self.x_positioncalc * (-1))+self.center_of_world[1]
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=2
                time.sleep(1)
        if self.count==2:
            print("--- --- ---3. checkpointe gidiliyor.")
            self.x_positioncalc=self.center_of_world[0]
            self.y_positioncalc=(self.x_positioncalc * (-1))+self.center_of_world[1]
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=3
                time.sleep(1)
        if self.count==3:
            print("--- --- --- ---4. checkpointe gidiliyor.")
            self.x_positioncalc=(self.searchId * (self.aramaAraligi * -1))+self.center_of_world[0]
            self.y_positioncalc=(self.x_positioncalc * (-1))+self.center_of_world[1]
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=4
                time.sleep(1)
        if self.count==4:
            print("--- --- --- --- ---5. checkpointe gidiliyor.")
            self.x_positioncalc=(self.searchId * (self.aramaAraligi * -1))+self.center_of_world[0]
            self.y_positioncalc=self.center_of_world[1]
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=5
                time.sleep(1)
        if self.count==5:
            print("--- --- --- --- --- ---6. checkpointe gidiliyor.")
            self.x_positioncalc=(self.searchId * (self.aramaAraligi * -1))+self.center_of_world[0]
            self.y_positioncalc=(self.searchId * self.aramaAraligi)+self.center_of_world[1]
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=6
                time.sleep(1)
        if self.count==6:
            print("--- --- --- --- --- --- ---7. checkpointe gidiliyor.")
            self.x_positioncalc=self.center_of_world[0]
            self.y_positioncalc=(self.searchId * self.aramaAraligi)+self.center_of_world[1]
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=7
                time.sleep(1)
        if self.count==7:
            print("--- --- --- --- --- --- --- ---8. checkpointe gidiliyor.")
            self.x_positioncalc=(self.searchId * self.aramaAraligi) +self.center_of_world[1]
            self.y_positioncalc=(self.searchId * self.aramaAraligi)+self.center_of_world[0]
            if self.yurukulum(data,self.x_positioncalc,self.y_positioncalc,self.searchAltitude)==True:
                self.count=8
                time.sleep(1)
        if self.count==8:
            self.searchId=self.searchId + 1
            self.count=0

        self.yaraliVarmi(data)

        if self.icerdeMisin(data,params,self.x_positioncalc,self.x_positioncalc)==True:
            self.count=self.count+1

            #mesafe olcerworldsize
    def mesafe(self,data,hedefx,hedefy):
        #eklendi
        self.xkonum=data["active_uav"]["location"][0]
        self.ykonum=data["active_uav"]["location"][1]
        mesafe =(self.xkonum-hedefx)**2 + (self.ykonum-hedefy)**2
        mesafe = math.sqrt(mesafe)
        return mesafe
        #gez
    def yurukulum(self,data,hedefx,hedefy,yukseklik):
        print(self._uav_id)
        #eklendi
        self.xkonum=data["active_uav"]["location"][0]
        self.ykonum=data["active_uav"]["location"][1]
        angle=self.yonBul(data,hedefx,hedefy)
        mesafe =(self.xkonum-hedefx)**2 + (self.ykonum-hedefy)**2
        mesafe = math.sqrt(mesafe)
        speed = self.speedcalc(data,hedefx,hedefy)
        if speed==-1:
            self.send_move_cmd(0,0,angle,yukseklik)
        elif not speed==0:
            self.send_move_cmd(speed,0,angle,yukseklik)
            print("-------",self._uav_id)
            print("mesafe =",int(mesafe))
            print("hiz =",speed)
            print("aci =",self.heading)
            print("konumx =",self.xkonum)
            print("konumy =",self.ykonum)
            print("hedef konumx =",hedefx)
            print("hedef konumy =",hedefy)
            return False

        else:
            return True
            #hiz hesabi
    def speedcalc(self,data,hedefx,hedefy):
        a_x=data["active_uav"]["location"][0]
        a_y=data["active_uav"]["location"][1]
        dist_x=hedefx-a_x
        dist_y=hedefy-a_y
        dist_x=dist_x**2
        dist_y=dist_y**2
        mesafe=math.sqrt(dist_x+dist_y)
        if self.distance_from_crash_point(data):
            return -1
        #mesafelere bagli olarak oran degisikligi
        if mesafe>1000:
            speed=140
        if mesafe<1400:
            speed=30
        if mesafe<600:
            speed=25
        if mesafe<250:
            speed=20
        if mesafe<20:
            speed=(mesafe*0.4)
        if mesafe<15:
            speed=(mesafe*0.15)
        if mesafe<8:
            speed=0
        self.speed=speed
        return speed

    def gps_arangement(self,data):
        print(data["active_uav"]["x_speed"],data["active_uav"]["y_speed"],data["active_uav"]["heading"],data["active_uav"]["altitude"])
        if self.gps[0] == [0,0,0,0]:
            self.gps[0] = data["active_uav"]["x_speed"],data["active_uav"]["y_speed"],data["active_uav"]["heading"],data["active_uav"]["altitude"]
        else:
            self.gps[1] = data["active_uav"]["x_speed"],data["active_uav"]["y_speed"],data["active_uav"]["heading"],data["active_uav"]["altitude"]
            #dosya[0] i kullan
            if data["uav_guide"]["gps_noise_flag"] == True:
                self.send_move_cmd(data["uav_guide"]["speed"]["x"],self.gps[0][1],self.gps[0][2],self.gps[0][3])
            else:
                self.gps[0] = self.gps[1]

    def tall_building(self,params):
        tall_loc=[0,0,0,0]
        tall_locs=[]
        for i in range (len(params["special_assets"])):
            if params["special_assets"][i]["type"]=="tall_building":
                tall_adet=len(params["special_assets"][i]["locations"])
                break
        for j in range(tall_adet-1):
            tall_locs.append(0)
            tall_loc_x=params["special_assets"][i]["locations"][j][0]
            tall_loc_y=params["special_assets"][i]["locations"][j][1]
            tall_wid_x=params["special_assets"][i]["width"][0]/1.5
            tall_wid_y=params["special_assets"][i]["width"][1]/1.5
            tall_loc[0]=tall_loc_x-tall_wid_x,tall_loc_y-tall_wid_y
            tall_loc[0]=list(tall_loc[0])
            tall_loc[1]=tall_loc_x-tall_wid_x,tall_loc_y+tall_wid_y
            tall_loc[1]=list(tall_loc[1])
            tall_loc[2]=tall_loc_x+tall_wid_x,tall_loc_y+tall_wid_y
            tall_loc[2]=list(tall_loc[2])
            tall_loc[3]=tall_loc_x+tall_wid_x,tall_loc_y-tall_wid_y
            tall_loc[3]=list(tall_loc[3])
            tall_loc=list(tall_loc)
            tall_locs[j]=[tall_loc[0],tall_loc[1],tall_loc[2],tall_loc[3]]
        return tall_locs

    def aralikBelirle(self,data,params):
        worldLenght=params["world_length"]
        worldWidth=params["world_width"]
        worldsize=(worldLenght+worldWidth) / 2
        self.aramaAraligi=worldsize/params["uav_count"]
        self.aramaAraligi=self.aramaAraligi/2

    #denied sorgusu
    def icerdeMisin(self,data,params,x,y):
        zones=self.tall_buildings
        for j in range(len(params["denied_zones"])):
            zones.append(params["denied_zones"][j])
        for i in range(len(zones)):
            #print(self.tall_buildings)
            #print(params["denied_zones"][i])
            polygon=zones[i]
            points =[[x,y]]#kontrol noktasi
            path = mpltPath.Path(polygon)
            inside = path.contains_points(points)#icinde mi
            return inside


    #noktalar olusturuluyor
    def alandaMisin(self,data,params,x,y):
        #polygon = params["denied_zones"][0]#koseler
        polygon=params["world_boundaries"]
        points =[[x,y]]#kontrol noktasi
        path = mpltPath.Path(polygon)
        inside = path.contains_points(points)#icinde mi
        return inside

    def kontrolNoktalar(self,data):
        ref_Points=[0,0,0,0]
        a_k=data["active_uav"]["heading"]
        a_k=math.radians(a_k)
        sin_ak=math.sin(a_k)
        cos_ak=math.cos(a_k)
        uav_x=data["active_uav"]["location"][0]
        uav_y=data["active_uav"]["location"][1]
        uav_x=uav_x+cos_ak*5
        uav_y=uav_y+sin_ak*5
        ref=[uav_x,uav_y]
        #4. nokta 90 derece sol noktamiz !!!5m iceride kalacak nokta!!!
        ref_Points[0]=ref
        uav_x=data["active_uav"]["location"][0]
        uav_y=data["active_uav"]["location"][1]
        uav_x=uav_x+sin_ak*10
        uav_y=uav_y-cos_ak*10
        ref=[uav_x,uav_y]
        #2. nokta burnumuz !!!disarda kalacak nokta!!!
        ref_Points[1]=ref

        uav_x=data["active_uav"]["location"][0]
        uav_y=data["active_uav"]["location"][1]
        uav_x=uav_x+sin_ak*20
        uav_y=uav_y-cos_ak*20
        ref=[uav_x,uav_y]
        #3.nokta burnumuzun 2 metre onu !!!disarda kalacak nokta!!!
        ref_Points[2]=ref

        uav_x=data["active_uav"]["location"][0]
        uav_y=data["active_uav"]["location"][1]
        uav_x=uav_x+cos_ak*20
        uav_y=uav_y+sin_ak*20
        ref=[uav_x,uav_y]
        #4. nokta 90 derece sol noktamiz !!!iceride kalacak nokta!!!
        ref_Points[3]=ref
        return ref_Points

    def deniedZoneDocMekaniks(self,data,params):
        noktalar=self.kontrolNoktalar(data)
        #daha once varis noktasi olusturulmadiysa varis noktasi olusturuluyor...
        if self.icerdeMisin(data,params,noktalar[2][0],noktalar[2][1]) and self.denied_varis_bulundu:
            heading=data["active_uav"]["heading"]
            altitude=data["active_uav"]["altitude"]
            self.send_move_cmd(0,0,heading,altitude)
            print("daha once varis noktasi olusturulmamis")
            z=params["denied_zones"][0]
            max=0
            max_corner=[0,0]
            for i in range(len(params["denied_zones"][0])):
                print("denied zone distleri karsilastiriliyor",i)
                uav_x=data["active_uav"]["location"][0]
                uav_y=data["active_uav"]["location"][1]
                dist=(uav_x-z[i][0])**2+(uav_y-z[i][1])**2
                dist=math.sqrt(dist)
                if dist>max:
                    max=dist
            print("max uzak nokta bulundu")
            a_k=data["active_uav"]["heading"]
            a_k=math.radians(a_k)
            sin_ak=math.sin(a_k)
            cos_ak=math.cos(a_k)
            uav_x=uav_x+sin_ak*max #en uzak nokta belirlenir.
            uav_y=uav_y-cos_ak*max
            print(uav_x,uav_y)
            while self.icerdeMisin(data,params,uav_x,uav_y)==False and self.denied_varis_bulundu:
                uav_x=uav_x+sin_ak*-1 #en uzak nokta belirlenir.
                uav_y=uav_y-cos_ak*-1
                self.denied_varis=[uav_x,uav_y]
            print("varis noktasi bulundu")
            self.denied_varis_bulundu=False
        else:
            return None


    def DeniedZoneDocMekaniksStart(self,data,params):
        kontrol=self.kontrolNoktalar(data)
        altitude=data["active_uav"]["altitude"]

        #tum noktalar disarda= varis noktasina git!!
        if self.icerdeMisin(data,params,kontrol[2][0],kontrol[2][1])==False and self.icerdeMisin(data,params,kontrol[3][0],kontrol[3][1])==False :

            heading=self.yonBul(data,self.denied_varis[0],self.denied_varis[1])
            self.send_move_cmd(5,0,heading,altitude)
        #ondeki nokta icerde sol nokta disarda= saga don
        if self.icerdeMisin(data,params,kontrol[2][0],kontrol[2][1])==True and self.icerdeMisin(data,params,kontrol[3][0],kontrol[3][1])==False:

            heading=data["active_uav"]["heading"]
            heading=heading-5
            self.send_move_cmd(0,0,heading,altitude)
        #ondeki nokta disarda sol nokta icerde=letsgoo
        if self.icerdeMisin(data,params,kontrol[2][0],kontrol[2][1])==False and self.icerdeMisin(data,params,kontrol[3][0],kontrol[3][1])==True:
            y_speed=0
            if self.icerdeMisin(data,params,kontrol[0][0],kontrol[0][1])==True:

                y_speed=2
            heading=data["active_uav"]["heading"]

            self.send_move_cmd(5,y_speed,heading,altitude)
            #noktalarin 2side icerdeyse=don
        if self.icerdeMisin(data,params,kontrol[2][0],kontrol[2][1])==True and self.icerdeMisin(data,params,kontrol[3][0],kontrol[3][1])==True:

            heading=data["active_uav"]["heading"]
            heading=heading-5
            self.send_move_cmd(0,0,heading,altitude)
        if self.icerdeMisin(data,params,kontrol[0][0],kontrol[0][1])==True:

            heading=data["active_uav"]["heading"]

#kullanilmiyorrrrr
    def denied_move(self,data,x,y):
        angle=self.yonBul(data,x,y)
        instant_location_x=data["active_uav"]["location"][0]
        instant_location_y=data["active_uav"]["location"][1]
        mesafe =(instant_location_x-x)**2 + (instant_location_y-y)**2
        mesafe = math.sqrt(mesafe)
        altitude=data["active_uav"]["altitude"]
        speed=20
        if mesafe>50:
            speed=mesafe*0.25
        if mesafe>75:
            speed=mesafe*0.10
        if mesafe>10:
            speed=mesafe*0.05
        self.send_move_cmd(speed,0,angle,100)

    def fallback(self,data,params):
        x=self.starting_location[0]
        y=self.starting_location[1]
        instant_location_x=data["active_uav"]["location"][0]
        instant_location_y=data["active_uav"]["location"][1]
        mesafe =(instant_location_x-x)**2 + (instant_location_y-y)**2
        mesafe = math.sqrt(mesafe)
        print(mesafe)
        if self.uav_fuel_error==False:

            width=params["world_width"]
            length=params["world_length"]
            length=width**2+length**2
            length=math.sqrt(length)
            if self.alandaMisin(data,params,instant_location_x,instant_location_y):
                fuel=length*(1/self.speed_15_gidilen_yol)+mesafe*(1/self.speed_60_gidilen_yol)
            if self.alandaMisin(data,params,instant_location_x,instant_location_y)==False:
                fuel=mesafe*(1/self.speed_60_gidilen_yol)

            if fuel>=data["active_uav"]["fuel_reserve"]:
                self.uav_fuel_error=True#benzinnnnnn bittiiiiiiiiiiiiiiiiiiiiiii knkkkkkkkkkk
        if self.uav_fuel_error and self.alandaMisin(data,params,instant_location_x,instant_location_y):
            heading=self.yonBul(data,x,y)
            altitude=101+((self._uav_id+1)*self.uav_height)
            speed = 0
            if data["active_uav"]["altitude"]>100+self.uav_height:
                speed=15
            self.send_move_cmd(speed,0,heading,altitude)
        if self.uav_fuel_error and self.alandaMisin(data,params,instant_location_x,instant_location_y)==False:
            heading=self.yonBul(data,x,y)
            altitude=101+((self._uav_id+1)*self.uav_height)
            speed = 60
            if mesafe<=236 and mesafe>=3:
                speed = 0
            if mesafe<3:
                altitude = self.starting_altitude
                speed=0
            self.send_move_cmd(speed,0,heading,altitude)

    def altitude_control(self,data):
        #uav_collision_distance = data["active_uav"]["x_speed"] * self.range_rate
        crash_point_x=data["active_uav"]["location"][0]
        crash_point_y=data["active_uav"]["location"][1]
        for i in range (len(data["uav_link"])):
            uav_loc_x=data["uav_link"][i].values()[0]["location"][0]
            uav_loc_y=data["uav_link"][i].values()[0]["location"][1]
            uav_altitude=data["uav_link"][i].values()[0]["altitude"]
            alti_dist=uav_altitude-data["active_uav"]["altitude"]
            alti_dist=math.fabs(alti_dist)
            dist=(crash_point_x - uav_loc_x)**2 + (crash_point_y - uav_loc_y)**2
            dist=math.sqrt(dist)
            if dist<4 and alti_dist<5:
                return 0
            if dist<14:
                return uav_altitude
        #eger hic ucak yoksa etrafta 0 donecek
        return 0


#ondeki araclara yol veriyor
    def distance_from_crash_point(self,data):
        uav_collision_distance = data["active_uav"]["x_speed"] * self.range_rate
        if uav_collision_distance <15:
            uav_collision_distance=15
        angle=data["active_uav"]["heading"]
        angle=math.radians(angle)
        sin_angle=math.sin(angle)
        cos_angle=math.cos(angle)
        crash_point_x=data["active_uav"]["location"][0]+(sin_angle*self.uav_front)
        crash_point_y=data["active_uav"]["location"][1]-(cos_angle*self.uav_front)
        for i in range (len(data["uav_link"])):
            if int(data["uav_link"][i].values()[0]["location"][0]) != int(data["active_uav"]["location"][0]) and int(data["uav_link"][i].values()[0]["location"][1]) != int(data["active_uav"]["location"][1]):
                uav_loc_x=data["uav_link"][i].values()[0]["location"][0]
                uav_loc_y=data["uav_link"][i].values()[0]["location"][1]
                dist=(crash_point_x - uav_loc_x)**2 + (crash_point_y - uav_loc_y)**2
                dist=math.sqrt(dist)
                target_altitude=data["uav_link"][i].values()[0]["altitude"]

                altitude_range=math.fabs(data["active_uav"]["altitude"]-target_altitude)
                if dist < uav_collision_distance  and altitude_range < self.uav_height:
                    return True
        return False
#kullanilmiyorrrrr.
    def dist_from_node(self,data):
        instant_location_x=data["active_uav"]["location"][0]
        instant_location_y=data["active_uav"]["location"][1]
        #liste sayisi duzenlenmeli!
        for i in range(len(data["uav_link"])):
            a=data["uav_link"][i].keys()
            uav_name=a[0][4]
            uav_name=str(uav_name)
            #print(int(uav_name),type(uav_name))
            if uav_name != self.uav_id:
                location=data["uav_link"][i].values()
                uav_loc_x=location[0]["location"][0]
                uav_loc_y=location[0]["location"][1]
                dist=(instant_location_x - uav_loc_x)**2 + (instant_location_y - uav_loc_y)**2
                dist=math.sqrt(dist)

                #print(dist,"slmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")

                if dist < self.uav_collision_distance:
                    return i

    def merkeziBul(self,params):
        points=params["world_boundaries"]
        top_x=0
        top_y=0
        for i in range(len(points)):
            top_x=points[i][0]+top_x
            top_y=points[i][1]+top_y
        top_x=top_x/len(points)
        top_y=top_y/len(points)
        return [top_x, top_y]

#gitmemiz gereken lokasyona bakiyor.
    def yonBul(self,data,x,y):

        fark=[0,0]
        uav_x=data["active_uav"]["location"][0]
        uav_y=data["active_uav"]["location"][1]
        fark[0]=x-uav_x
        # 90 derece farki icin -y
        fark[1]=uav_y-y
        aci=math.atan2(fark[0],fark[1])
        angle=math.degrees(aci)
        return angle
#dinamik mesafeye bagli hiz degisikligi
    def speed(self,data):
        #print("slm")
        guide_x=data["uav_guide"]["location"][0]
        guide_y=data["uav_guide"]["location"][1]
        #print("slm",guide_x)
        a_x=data["active_uav"]["location"][0]
        a_y=data["active_uav"]["location"][1]
        dist_x=guide_x-a_x
        dist_y=guide_y-a_y
        dist_x=dist_x**2
        dist_y=dist_y**2
        mesafe=math.sqrt(dist_x+dist_y)

        #mesafelere bagli olarak oran degisikligi
        speed=data["uav_guide"]["speed"]["x"]

        x_speed=mesafe/speed+speed
        if mesafe<8:
            x_speed=speed

        # if mesafe>500:
        #     x_speed=speed+(mesafe*0.1)
        # if mesafe>200 and mesafe<500:
        #     x_speed=speed+(mesafe*0.05)
        # if mesafe>75 and mesafe<200:
        #     x_speed=speed+(mesafe*0.03)
        # if mesafe>25 and mesafe<75:
        #     x_speed=speed+(mesafe*0.02)
        # if mesafe>5 and mesafe<25:
        #     x_speed=speed+(mesafe*0.01)
        # if mesafe<5:
        #     x_speed=speed
        #yukseklik 10 dan kucukse hiz yapma
        if data["active_uav"]["altitude"]<10:
            return 0
        return x_speed
#istenilen konuma gidip durduran fonks.
    def move(self,data,x,y,altitude):
        angle=self.yonBul(data,x,y)
        instant_location_x=data["active_uav"]["location"][0]
        instant_location_y=data["active_uav"]["location"][1]
        mesafe =(instant_location_x-x)**2 + (instant_location_y-y)**2
        mesafe = math.sqrt(mesafe)
        if mesafe+self.formation_distance_tolerance < 50:
            if data["active_uav"]["altitude"]<10:
                x_speed=0
                self.send_move_cmd(x_speed,0,angle,altitude)
            else:
                x_speed=mesafe*0.25
                self.send_move_cmd(x_speed,0,angle,altitude)

        if mesafe+self.formation_distance_tolerance >= 50:
            if data["active_uav"]["altitude"]<10:
                x_speed=0
                self.send_move_cmd(x_speed,0,angle,altitude)
            else:
                x_speed=20
                self.send_move_cmd(x_speed,0,angle,altitude)

#formasyon sirasinda hareket fonks.
    def formation_move(self,data,x,y,altitude):
        angle=data["active_uav"]["heading"]
        x_speed=data["active_uav"]["x_speed"]
        #print("hiz=",x)
        instant_location_x=data["active_uav"]["location"][0]
        instant_location_y=data["active_uav"]["location"][1]
        if data["uav_guide"]["gps_noise_flag"] == True:
            loc=self.noise_filter(data)
            instant_location_x=loc[0]
            instant_location_y=loc[1]
        #print(instant_location_x,instant_location_y)
        mesafe =(instant_location_x-x)**2 + (instant_location_y-y)**2
        mesafe = math.sqrt(mesafe)
        angle=self.yonBul(data,x,y)
        x_speed=self.speed(data)
        # pugachev's cobra  ucak aniden yavaslayarak noktanin onumuzde kalmasini saglar
        if  self.square and self.arrow:
            print("degissssssssssssssssssssssssssssssss")
            a_k=data["uav_formation"]["a_k"]
            x_speed= data["uav_guide"]["speed"]["x"]
            x_speed=x_speed*0.50
            self.send_move_cmd(x_speed,0,a_k,altitude)
            time.sleep(5)
            self.arrow=False
            self.square=False
        if mesafe <8:
            angle=angle + data["active_uav"]["heading"]
            angle = angle /2
            x_speed = data["uav_guide"]["speed"]["x"] - 1


        # if mesafe <= self.formation_distance_tolerance:
        #     speed_x = data["uav_guide"]["speed"]["x"]
        #     speed_y = data["uav_guide"]["speed"]["y"]
        #     speed_x=math.sqrt((speed_x**2)+(speed_y**2))
        #     self.send_move_cmd(speed_x,0,angle,altitude)
        if self.distance_from_crash_point(data):
            print(self.uav_id,"firene basss")
            self.send_move_cmd(0,0,angle,altitude)
            #print(self.uav_id,data["active_uav"]["x_speed"])
        else:
            self.send_move_cmd(x_speed,0,angle,altitude)

#ok basi fonks.
    def FormationFlyArrow(self,data):
        self.arrow=True
        u_b=data["uav_formation"]["u_b"]
        a_b=data["uav_formation"]["a_b"]
        u_k=data["uav_formation"]["u_k"]
        a_k=data["uav_formation"]["a_k"]
        guide_x=data["uav_guide"]["location"][0]
        guide_y=data["uav_guide"]["location"][1]
        a_k=math.radians(a_k)
        sin_ak=math.sin(a_k)
        cos_ak=math.cos(a_k)
        uav_y=guide_y+(cos_ak*u_k)
        uav_x=guide_x-(sin_ak*u_k)
        guide_altitude=data["uav_guide"]["altitude"]
        altitude=guide_altitude
        alti_ctrl=self.altitude_control(data)
        if alti_ctrl!=0:
            if alti_ctrl>altitude and data["active_uav"]["altitude"]>alti_ctrl:
                altitude=alti_ctrl+self.uav_height
            if alti_ctrl<altitude and data["active_uav"]["altitude"]<alti_ctrl:
                altitude=alti_ctrl-self.uav_height


        #sin_ab=math.sin(a_b)
        #cos_ab=math.cos(a_b)
        #ub_x=sin_ab*u_b
        #ub_y=cos_ab*u_b
        #formasyon basindaki iha konumu
        if self._uav_id==0:
            if data["uav_guide"]["speed"]["x"] == 0:
                return self.move(data,uav_x,uav_y,altitude)
            #print("formasyon",guide_x,guide_y)
            #print("slm",uav_x,uav_y)
            #print(self.uav_id,"=",uav_x,uav_y)
            #self.yonBul(data,uav_x,uav_y)
            #print(self.uav_id,"=",uav_x,uav_y)
            #klavuzun sol arkasinda kalan ekip id numasindan seciliyor
        if self._uav_id%2==0 and self._uav_id!=0:
            a_k=data["uav_formation"]["a_k"]
            a_k=a_k+a_b
            a_k=math.radians(a_k)
            sin_ak=math.sin(a_k)
            cos_ak=math.cos(a_k)
            dim=self._uav_id//2
            uav_y=uav_y+(cos_ak*u_b*dim)
            uav_x=uav_x-(sin_ak*u_b*dim)
            if self.first_move :
                time.sleep(dim*9)
                self.first_move=False
            if data["uav_guide"]["speed"]["x"]==0:
                return self.move(data,uav_x,uav_y,altitude)
            #klavuzun sol arka sirasi konumlandiriliyor.
            #klavuzun sag arkasinda kalan ekip id numasindan seciliyor.
        if self._uav_id%2==1:
            #klavuzun sag arka sirasi konumlandiriliyor.
            a_k=data["uav_formation"]["a_k"]
            a_k=a_k-a_b
            a_k=math.radians(a_k)
            sin_ak=math.sin(a_k)
            cos_ak=math.cos(a_k)
            dim=(self._uav_id+1)//2

            uav_y=uav_y+(cos_ak*u_b*dim)
            uav_x=uav_x-(sin_ak*u_b*dim)
            if self.first_move :
                time.sleep(dim*9)
                self.first_move=False
            if data["uav_guide"]["speed"]["x"]==0:
                return self.move(data,uav_x,uav_y,altitude)
            #klavuzun sol arka sirasi konumlandiriliyor.
            #print(self.uav_id,"=",uav_x,uav_y)
            #uav_x=guide_x+sin_ak*u_k+(ub_x*dim)
            #yukaridakinden farki saga dogru dizilirken konum cikariliyor
            #uav_y=guide_y+cos_ak*u_k-(ub_y*dim)

            #self.yonBul(data,uav_x,uav_y)
        self.formation_move(data,uav_x,uav_y,altitude)

#prizma fonks.
    def FormationFlySquare(self,data):
        self.square=True
        u_b=data["uav_formation"]["u_b"]#dronelar arasi uzaklik
        u_k=data["uav_formation"]["u_k"]#0 kilavuz arasi uzaklik
        a_k=data["uav_formation"]["a_k"]#pusula acisi
        guide_x=data["uav_guide"]["location"][0]
        guide_y=data["uav_guide"]["location"][1]
        guide_altitude=data["uav_guide"]["altitude"]
        a_k=math.radians(a_k)
        sin_ak=math.sin(a_k)
        cos_ak=math.cos(a_k)
        uav_y=guide_y+(cos_ak*u_k)
        uav_x=guide_x-(sin_ak*u_k)
        #print(data["uav_guide"]["gps_noise_flag"])
        if self._uav_id==0:
            altitude=guide_altitude
            if data["active_uav"]["altitude"]>=10:
                altitude=guide_altitude
            alti_ctrl=self.altitude_control(data)
            if alti_ctrl!=0:
                if alti_ctrl>altitude and data["active_uav"]["altitude"]>alti_ctrl:
                    altitude=alti_ctrl+self.uav_height
                if alti_ctrl<altitude and data["active_uav"]["altitude"]<alti_ctrl:
                    altitude=alti_ctrl-self.uav_height





            if data["uav_guide"]["speed"]["x"] == 0:
                return self.move(data,uav_x,uav_y,altitude)

        if self._uav_id%4==1:
            uav_y=uav_y+(cos_ak*u_b)
            uav_x=uav_x-(sin_ak*u_b)
            #sol
            uav_y=uav_y+(sin_ak*(u_b/2))
            uav_x=uav_x-(cos_ak*(u_b/2))
            #alt
            altitude=guide_altitude-(u_b/2)
            alti_ctrl=self.altitude_control(data)
            if alti_ctrl!=0:
                if alti_ctrl>altitude and data["active_uav"]["altitude"]>alti_ctrl:
                    altitude=alti_ctrl+self.uav_height
                if alti_ctrl<altitude and data["active_uav"]["altitude"]<alti_ctrl:
                    altitude=alti_ctrl-self.uav_height





            if altitude< 10:
                altitude=15
            dim=self._uav_id//5
            uav_x=uav_x-(sin_ak*u_b*(dim))
            uav_y=uav_y+(cos_ak*u_b*(dim))
            if self.first_move :
                time.sleep((dim+1)*9)
                self.first_move=False
            if data["uav_guide"]["speed"]["x"] == 0:
                return self.move(data,uav_x,uav_y,altitude)

        if self._uav_id%4==2:
            uav_y=uav_y+(cos_ak*u_b)
            uav_x=uav_x-(sin_ak*u_b)
            #sag
            uav_y=uav_y-(sin_ak*(u_b/2))
            uav_x=uav_x+(cos_ak*(u_b/2))
            #alt
            altitude=guide_altitude-(u_b/2)
            alti_ctrl=self.altitude_control(data)
            if alti_ctrl!=0:
                if alti_ctrl>altitude and data["active_uav"]["altitude"]>alti_ctrl:
                    altitude=alti_ctrl+self.uav_height
                if alti_ctrl<altitude and data["active_uav"]["altitude"]<alti_ctrl:
                    altitude=alti_ctrl-self.uav_height






            if altitude< 10:
                altitude=15
            dim=self._uav_id//5

            uav_x=uav_x-(sin_ak*u_b*(dim))
            uav_y=uav_y+(cos_ak*u_b*(dim))
            if self.first_move :
                time.sleep((dim+1)*9)
                self.first_move=False
            if data["uav_guide"]["speed"]["x"] == 0:
                return self.move(data,uav_x,uav_y,altitude)

        if self._uav_id%4==3:
            uav_y=uav_y+(cos_ak*u_b)
            uav_x=uav_x-(sin_ak*u_b)
            #sol
            uav_y=uav_y+(sin_ak*(u_b/2))
            uav_x=uav_x-(cos_ak*(u_b/2))
            #ust
            altitude=guide_altitude+(u_b/2)
            alti_ctrl=self.altitude_control(data)
            if alti_ctrl!=0:
                if alti_ctrl>altitude and data["active_uav"]["altitude"]>alti_ctrl:
                    altitude=alti_ctrl+self.uav_height
                if alti_ctrl<altitude and data["active_uav"]["altitude"]<alti_ctrl:
                    altitude=alti_ctrl-self.uav_height




            dim=self._uav_id//5

            uav_x=uav_x-(sin_ak*u_b*(dim))
            uav_y=uav_y+(cos_ak*u_b*(dim))
            if self.first_move :
                time.sleep((dim+1)*9)
                self.first_move=False
            if data["uav_guide"]["speed"]["x"] == 0:
                return self.move(data,uav_x,uav_y,altitude)

        if self._uav_id%4==0 and self._uav_id!=0:
            uav_y=uav_y+(cos_ak*u_b)
            uav_x=uav_x-(sin_ak*u_b)
            #sag
            uav_y=uav_y-(sin_ak*(u_b/2))
            uav_x=uav_x+(cos_ak*(u_b/2))
            #ust
            altitude=guide_altitude+(u_b/2)

            alti_ctrl=self.altitude_control(data)
            if alti_ctrl!=0:
                if alti_ctrl>altitude and data["active_uav"]["altitude"]>alti_ctrl:
                    altitude=alti_ctrl+self.uav_height
                if alti_ctrl<altitude and data["active_uav"]["altitude"]<alti_ctrl:
                    altitude=alti_ctrl-self.uav_height





            dim=self._uav_id//5
            uav_x=uav_x-(sin_ak*u_b*(dim))
            uav_y=uav_y+(cos_ak*u_b*(dim))
            if self.first_move :
                time.sleep((dim+1)*9)
                self.first_move=False
            if data["uav_guide"]["speed"]["x"] == 0:
                return self.move(data,uav_x,uav_y,altitude)
        self.formation_move(data,uav_x,uav_y,altitude)


default_ip = '127.0.0.1'
default_port = 5672

def get_uav_id():
    uav_id = sys.argv[1]
    try:
        uav_id = int(uav_id)
    except ValueError:
        print('ERROR: Invalid UAV id:' + sys.argv[1])
        sys.exit(1)
    return str(uav_id)


def get_ip():
    if len(sys.argv) > 2:
        return sys.argv[2]
    else:
        return default_ip


def get_port():
    if len(sys.argv) > 3:
        port_num = sys.argv[3]
        try:
            port_num = int(port_num)
        except ValueError:
            print('ERROR: invalid port number:' + sys.argv[3])
            sys.exit(2)

        return port_num
    else:
        return default_port


if __name__ == '__main__':
    # uav id al
    uav_id = get_uav_id()
    ip = get_ip()
    port = get_port()
    uav = KAGUAV(uav_id, ip, port)
    uav.start_listening()
    #eklemee
