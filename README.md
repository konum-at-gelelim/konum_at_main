# konum_at_main
# main.py Furkan Güneştaş, Mümin Can Uçak ve Eren Güneştaş'ın ortak çalışmasıdır.
#aşşağıdaki json paketleri göz alınarak hazırlanmıştır.


# iha durum ve iha zincir bilgi paketi
{
  "active_uav":
  {
    "location":"39.924980,32.836794",
    "altitude":"1000",
    "heading":"30.0",
    "speed":{
      "x":"60.0",
      "y":"10.0"
      </br>
      },
      "fuel_reserve":"%100.0",
      "sensors":{
        "logical_camera":
        {"detected":[
        {
          "type":"casualty",
          "status":"injured",
          "pose":"39.924980,32.841231"
          },
          {
            "type":"casualty",
            "status":"healthy",
            "pose":"39.944980,32.836794"
          }
        ]
      }
    },
    "equipments":{
      "telecom_beacon":{
        "telecom_served_people_count":5
        }
      }
    },
    "uav_link":{
      "uav_1":{
        "location":"39.924980,32.836794",
        "altitude":"1000",
        "heading":"30.0",
        "speed":{
          "x":"60.0",
          "y":"10.0"
         }
        },
        "uav_2":{
          "location":"39.924980,32.836794"
          ,"altitude":"1000",
          "heading":"30.0",
          "speed":{
            "x":"60.0",
            "y":"10.0"
            }
          },
          "uav_3":{
            "location":"39.924980,32.836794",
            "altitude":"1000",
            "heading":"30.0",
            "speed":{
              "x":"60.0",
              "y":"10.0"
            }
          }
        },
        "hospitals_in_range":[
        {
          "location":"39.933155,32.822292",
          "hospital_quota":10
        }
      ],
      "uav_guide":{  
        "location":"39.924980, 32.836794",
        "altitude":"1000",
        "heading":"30.0",
        "speed":{  
          "x":"60.0",
          "y":"10.0"
          }
                  "dispatch": False,
        },"uav_formation": {
          "type": "arrow",
          "u_b": "25.0",
          "u_a": "30.0",
          "u_k": "25.0",
          "a_k": "45.0"
    }
}

# Simülasyon ortam parametre paketi
{
  "sim_env_parameters":{
    "level_difficulty":1,
    "injured_pick_up_duration":30,
    "injured_pick_up_height":"15.0",
    "injured_release_duration":30,
    "injured_release_height":"15.0",
    "uav_communication_range":"1000.0",
    "uav_count":10,
    "telecom_radius":"500.0",
    "telecom_height_max":"750.0",
    "telecom_height_min":"50.0",
    "world_width":"5000.0",
    "world_length":"5000.0",
    "logical_camera_height_max":"500.0",
    "logical_camera_height_min":"50.0",
    "logical_camera_pitch":"60.0",
    "logical_camera_horizontal_fov":"60.0"
    },
    "special_assets":[
    {
      "type":"hospital",
      "location":"39.933155,32.822292",
      "height":40
    },
      {
        "type":"hospital",
        "location":"39.920826,32.842875",
        "height":40
      },
      {
        "type":"tall_building",
        "location":"39.920826,32.842875",
        "height":70
      }
      ],
      "denied_zones":[
      {
        "zone_1":[
        "39.91539332.845461",
        "39.91801232.846343",
        "39.91676532.850036",
        "39.91503732.848852"
        ]
      }         
    ]</br></br>
}
