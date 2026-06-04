def load_configData()->dict:
    """
    This function loads the configuration data for different use cases, including their frequency, last run time, deadline, date mask, length of date, last loaded files, file frequency, sender type, pipeline name, data files, and raw data path.
    Returns:dict"""

    use_case_with_freq = {
        "erogazione_offerte": {
            "frequency": "D",
            "last_run":None,
            "Deadline":None,
            "Date_mask":"yyyyMMdd",
            "length_of_date":8,
            "last_loaded_files":[],
            "file_frequency":"",
            "sender_type":"",       #Sender Type: sharepoint directory (user) or external system
            "pipeline_name":"erogazione_offerte",
            "data_files": {
                "SubDirectory1": [
                    "Inpurfile1.csv",
                    "Inpurfile2_yyyyMMdd.csv",
                    "Inpurfile3_yyyyMMdd.csv"
                ]
                ,
              "SubDirectory2": [
                    "Inpurfile1.csv",
                    "Inpurfile2_yyyyMMdd.csv",
                    "Inpurfile3_yyyyMMdd.csv"
                ]
            },
            "Raw_Data_Path": "/RAES/ErogazioneOfferte/"
        }
    }

    return use_case_with_freq