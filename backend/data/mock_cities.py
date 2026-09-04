"""
settle — Mock City Dataset

A small, realistic dataset of Indian cities with livability metrics.
This will be replaced by database queries once PostgreSQL is integrated.

Data is intentionally varied to demonstrate filtering and comparison.
"""

MOCK_CITIES = [
    {
        "id": "bangalore",
        "name": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "population": 12800000,
        "lat": 12.9716,
        "lng": 77.5946,
        "safety_score": 6.5,
        "air_quality_index": 89,
        "avg_rent": 25000,
        "commute_score": 5.5,
        "cost_of_living_index": 7.2,
        "healthcare_score": 8.0,
        "education_score": 8.5,
        "localities": [
            {
                "id": "indiranagar",
                "name": "Indiranagar",
                "lat": 12.9784,
                "lng": 77.6408,
                "safety_score": 8.5,
                "air_quality_index": 92,
                "avg_rent": 35000,
                "commute_score": 6.0,
                "cost_of_living_index": 8.5,
                "healthcare_score": 8.5,
                "education_score": 8.0,
            },
            {
                "id": "hsr-layout",
                "name": "HSR Layout",
                "lat": 12.9121,
                "lng": 77.6446,
                "safety_score": 8.0,
                "air_quality_index": 85,
                "avg_rent": 28000,
                "commute_score": 7.0,
                "cost_of_living_index": 7.5,
                "healthcare_score": 8.0,
                "education_score": 8.5,
                "nearby_services": {
                    "hospitals": [
                        {"name": "Narayana Multispeciality", "lat": 12.9110, "lng": 77.6450},
                        {"name": "Greenview Medical", "lat": 12.9140, "lng": 77.6430}
                    ],
                    "schools": [
                        {"name": "National Public School", "lat": 12.9100, "lng": 77.6470},
                        {"name": "VIBGYOR High", "lat": 12.9135, "lng": 77.6420}
                    ],
                    "supermarkets": [
                        {"name": "Star Market", "lat": 12.9125, "lng": 77.6440},
                        {"name": "More Supermarket", "lat": 12.9115, "lng": 77.6465}
                    ],
                    "parks": [
                        {"name": "Agara Lake Park", "lat": 12.9180, "lng": 77.6410},
                        {"name": "Sector 3 Park", "lat": 12.9110, "lng": 77.6435}
                    ]
                }
            },
            {
                "id": "koramangala",
                "name": "Koramangala",
                "lat": 12.9352,
                "lng": 77.6245,
                "safety_score": 7.5,
                "air_quality_index": 105,
                "avg_rent": 30000,
                "commute_score": 5.5,
                "cost_of_living_index": 8.0,
                "healthcare_score": 8.5,
                "education_score": 8.0,
                "nearby_services": {
                    "hospitals": [
                        {"name": "St. John's Medical College", "lat": 12.9320, "lng": 77.6220}
                    ],
                    "schools": [
                        {"name": "VIBGYOR High", "lat": 12.9360, "lng": 77.6260}
                    ],
                    "supermarkets": [
                        {"name": "Spencer's", "lat": 12.9340, "lng": 77.6250}
                    ],
                    "parks": [
                        {"name": "BDA Park", "lat": 12.9370, "lng": 77.6230}
                    ]
                }
            }
        ]
    },
    {
        "id": "mumbai",
        "name": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "population": 20700000,
        "lat": 19.0760,
        "lng": 72.8777,
        "safety_score": 6.0,
        "air_quality_index": 152,
        "avg_rent": 35000,
        "commute_score": 4.5,
        "cost_of_living_index": 8.5,
        "healthcare_score": 8.5,
        "education_score": 8.0,
        "localities": [
            {
                "id": "bandra",
                "name": "Bandra West",
                "lat": 19.0596,
                "lng": 72.8295,
                "safety_score": 8.5,
                "air_quality_index": 130,
                "avg_rent": 65000,
                "commute_score": 5.0,
                "cost_of_living_index": 9.5,
                "healthcare_score": 9.0,
                "education_score": 8.5,
                "nearby_services": {
                    "hospitals": [
                        {"name": "Lilavati Hospital", "lat": 19.0580, "lng": 72.8280},
                        {"name": "Holy Family", "lat": 19.0610, "lng": 72.8310}
                    ],
                    "schools": [
                        {"name": "Arya Vidya Mandir", "lat": 19.0590, "lng": 72.8290}
                    ],
                    "supermarkets": [
                        {"name": "Nature's Basket", "lat": 19.0595, "lng": 72.8300}
                    ],
                    "parks": [
                        {"name": "Jogger's Park", "lat": 19.0620, "lng": 72.8250},
                        {"name": "Carter Road Promenade", "lat": 19.0630, "lng": 72.8240}
                    ]
                }
            },
            {
                "id": "andheri",
                "name": "Andheri East",
                "lat": 19.1136,
                "lng": 72.8697,
                "safety_score": 6.5,
                "air_quality_index": 165,
                "avg_rent": 35000,
                "commute_score": 6.5,
                "cost_of_living_index": 7.5,
                "healthcare_score": 8.0,
                "education_score": 7.5,
                "nearby_services": {
                    "hospitals": [
                        {"name": "SevenHills Hospital", "lat": 19.1180, "lng": 72.8750}
                    ],
                    "schools": [
                        {"name": "Bombay Cambridge", "lat": 19.1150, "lng": 72.8700}
                    ],
                    "supermarkets": [
                        {"name": "Reliance Smart", "lat": 19.1140, "lng": 72.8680}
                    ],
                    "parks": [
                        {"name": "Mahakali Caves Park", "lat": 19.1250, "lng": 72.8720}
                    ]
                }
            }
        ]
    },
    {
        "id": "delhi",
        "name": "Delhi",
        "state": "Delhi",
        "country": "India",
        "population": 19000000,
        "lat": 28.6139,
        "lng": 77.2090,
        "safety_score": 5.0,
        "air_quality_index": 210,
        "avg_rent": 22000,
        "commute_score": 5.0,
        "cost_of_living_index": 7.0,
        "healthcare_score": 7.5,
        "education_score": 8.0,
    },
    {
        "id": "hyderabad",
        "name": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "population": 10000000,
        "lat": 17.3850,
        "lng": 78.4867,
        "safety_score": 7.0,
        "air_quality_index": 95,
        "avg_rent": 18000,
        "commute_score": 6.5,
        "cost_of_living_index": 6.0,
        "healthcare_score": 7.5,
        "education_score": 7.5,
    },
    {
        "id": "chennai",
        "name": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "population": 10900000,
        "lat": 13.0827,
        "lng": 80.2707,
        "safety_score": 7.5,
        "air_quality_index": 78,
        "avg_rent": 16000,
        "commute_score": 6.0,
        "cost_of_living_index": 5.8,
        "healthcare_score": 8.0,
        "education_score": 7.5,
    },
    {
        "id": "pune",
        "name": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "population": 7400000,
        "lat": 18.5204,
        "lng": 73.8567,
        "safety_score": 7.5,
        "air_quality_index": 85,
        "avg_rent": 15000,
        "commute_score": 6.5,
        "cost_of_living_index": 5.5,
        "healthcare_score": 7.0,
        "education_score": 8.5,
    },
    {
        "id": "kolkata",
        "name": "Kolkata",
        "state": "West Bengal",
        "country": "India",
        "population": 14900000,
        "lat": 22.5726,
        "lng": 88.3639,
        "safety_score": 6.0,
        "air_quality_index": 145,
        "avg_rent": 12000,
        "commute_score": 6.0,
        "cost_of_living_index": 4.5,
        "healthcare_score": 6.5,
        "education_score": 7.0,
    },
    {
        "id": "ahmedabad",
        "name": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "population": 8000000,
        "lat": 23.0225,
        "lng": 72.5714,
        "safety_score": 7.0,
        "air_quality_index": 120,
        "avg_rent": 13000,
        "commute_score": 7.0,
        "cost_of_living_index": 5.0,
        "healthcare_score": 6.5,
        "education_score": 7.0,
    },
]
