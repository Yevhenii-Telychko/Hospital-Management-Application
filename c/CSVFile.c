/**
 * @file main.c
 * @brief Main file for managing clients and generating bills.
 * @date 09.12.2023
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * @brief Maximum length for a line in the CSV file.
 */
#define MAX_LINE_LENGTH 256

/**
 * @struct Client
 * @brief Structure representing a client's information.
 */
typedef struct {
    int id; /**< Client ID. */
    char service_type[MAX_LINE_LENGTH]; /**< Type of service. */
    char first_name[MAX_LINE_LENGTH]; /**< First name of the client. */
    char last_name[MAX_LINE_LENGTH]; /**< Last name of the client. */
    char address[MAX_LINE_LENGTH]; /**< Address of the client. */
    int age; /**< Age of the client. */
    char sex[MAX_LINE_LENGTH]; /**< Gender of the client. */
    char illness[MAX_LINE_LENGTH]; /**< Illness of the client. */
    int room_number; /**< Room number assigned to the client. */
    char specialty[MAX_LINE_LENGTH]; /**< Medical specialty. */
    char doctor[MAX_LINE_LENGTH]; /**< Name of the doctor. */
    char date[MAX_LINE_LENGTH]; /**< Date of appointment. */
    char time[MAX_LINE_LENGTH]; /**< Time of appointment. */
    int nights; /**< Number of nights the client stays. */
    char service[MAX_LINE_LENGTH]; /**< Additional services requested. */
} Client;

/**
 * @struct Price
 * @brief Structure representing prices for various medical services.
 */
typedef struct {
    int childbirth_price; /**< Price for childbirth service. */
    int health_check_up_price; /**< Price for health check-up service. */
    int carpal_tunnel_operation; /**< Price for carpal tunnel operation service. */
    int ent_price; /**< Price for ENT service. */
    int ultrasound_price; /**< Price for ultrasound service. */
    int colonoscopy; /**< Price for colonoscopy service. */
    int mri_price; /**< Price for MRI service. */
    int room_price; /**< Price per night for room. */
} Price;

/**
 * @brief Helper function to count the number of newlines in a file.
 * @param filepath Path to the file.
 * @return The number of newlines in the file (excluding the header line).
 */
int countNewlines(char *filepath) {
    FILE *file = fopen(filepath, "r");
    if (!file) {
        perror("Error opening file");
        return -1;  // Return -1 to indicate an error
    }

    int count = 0;
    int ch;

    while ((ch = fgetc(file)) != EOF) {
        if (ch == '\n') {
            count++;
        }
    }

    fclose(file);
    return count - 1;  // Subtract 1 to exclude the header line
}

/**
 * @brief Helper function to process a CSV line and populate a Client structure.
 * @param line CSV line containing client information.
 * @param client Pointer to the Client structure to be populated.
 */
void processCSVLine(char line[], Client *client) {
    sscanf(line, "%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,]",
           &client->id, client->service_type, client->first_name, client->last_name,
           client->address, &client->age, client->sex, client->illness,
           &client->room_number, client->specialty, client->doctor,
           client->date, client->time, &client->nights, client->service);
}

/**
 * @brief Helper function to free memory allocated for clients.
 * @param clients Pointer to an array of Client structures.
 */
void freeClientsMemory(Client *clients) {
    free(clients);
}

/**
 * @brief Helper function to remove newline characters from a string.
 * @param str Input string.
 * @return New string without newline characters.
 */
char *removeNewlines(char *str) {
    int length = strlen(str);

    // Allocate memory for the new string
    char *newString = (char *) malloc(length + 1);

    if (newString == NULL) {
        perror("Memory allocation error");
        exit(EXIT_FAILURE);
    }

    // Iterate through the string
    int j = 0;
    for (int i = 0; i < length; i++) {
        // If a newline character is found, skip it
        if (str[i] != '\n') {
            newString[j++] = str[i];
        }
    }

    // Null-terminate the new string
    newString[j] = '\0';

    return newString;
}

/**
 * @brief Function to set headers in a file.
 * @param headers String containing header information.
 * @param filepath Path to the file.
 */
void setHeaders(char *headers, char *filepath) {
    FILE *fpt;
    fpt = fopen(filepath, "w+");

    if (fpt == NULL) {
        perror("Error opening file");
        return;
    }

    fprintf(fpt, "%s\n", headers);
    fclose(fpt);
}

/**
 * @brief Function to check if a file is empty.
 * @param filepath Path to the file.
 * @return 1 if the file is empty, 0 otherwise.
 */
int isFileEmpty(char *filepath) {
    FILE *fpt;
    fpt = fopen(filepath, "r");
    fseek(fpt, 0, SEEK_END);  // Move the file pointer to the end of the file
    long fileSize = ftell(fpt);  // Get the current position of the file pointer
    fclose(fpt);
    if (fileSize == 0) {
        // File is empty
        return 1;
    } else {
        // File is not empty
        return 0;
    }
}

/**
 * @brief Function to add a client to a file.
 * @param data String containing client information.
 * @param filepath Path to the file.
 */
void addClient(char *data, char *filepath) {
    FILE *fpt;
    fpt = fopen(filepath, "a");  // Open the file in append mode

    if (fpt == NULL) {
        perror("Error opening file");
        return;
    }

    fprintf(fpt, "%s\n", data);  // Add a new line with the provided data
    fclose(fpt);
}

/**
 * @brief Function to delete a client from a file.
 * @param filePath Path to the original file.
 * @param tempfilepath Path to a temporary file.
 * @param newFilePath Path to a history file.
 * @param idToDelete ID of the client to be deleted.
 */
void deleteClientFromFile(char *filePath, char *tempfilepath, char *newFilePath, char *idToDelete) {
    FILE *file = fopen(filePath, "r");
    FILE *tempfile = fopen(tempfilepath, "w");
    FILE *historyfile = fopen(newFilePath, "a");

    if (file == NULL || tempfile == NULL || historyfile == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    char line[MAX_LINE_LENGTH];

    // Read and write the header line
    fgets(line, sizeof(line), file);
    fputs(line, tempfile);
    if (isFileEmpty(newFilePath)) {
        setHeaders(
                "ID,service_type,first,last name,address,age,sex,illness,room_number,specialty,doctor,date,time,nights,service",
                newFilePath);
    }

    while (fgets(line, sizeof(line), file) != NULL) {
        char currentId[MAX_LINE_LENGTH];
        char *commaPos = strchr(line, ',');

        if (commaPos != NULL) {
            // Extract the current ID
            strncpy(currentId, line, commaPos - line);
            currentId[commaPos - line] = '\0';

            if (strcmp(currentId, idToDelete) == 0) {
                fputs(line, historyfile);
            } else {
                fputs(line, tempfile);
            }
        } else {
            // Handle improperly formatted lines here
            fprintf(stderr, "Error: Malformed line in the file\n");
        }
    }

    fclose(file);
    fclose(tempfile);
    fclose(historyfile);

    remove(filePath);
    rename(tempfilepath, filePath);
}

/**
 * @brief Function to update a line in a file.
 * @param filePath Path to the original file.
 * @param newFilePath Path to a temporary file.
 * @param newLine New content for the line.
 * @param id ID of the line to be updated.
 */
void updateLineInFile(char *filePath, char *newFilePath, char *newLine, char *id) {
    FILE *file = fopen(filePath, "r");
    FILE *tempFile = fopen(newFilePath, "w");

    if (file == NULL || tempFile == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    char line[MAX_LINE_LENGTH];

    while (fgets(line, sizeof(line), file) != NULL) {
        char currentId[MAX_LINE_LENGTH];
        char *commaPos = strchr(line, ',');

        if (commaPos != NULL) {
            // Extract the current ID
            strncpy(currentId, line, commaPos - line);
            currentId[commaPos - line] = '\0';

            if (strcmp(currentId, id) == 0) {
                fputs(newLine, tempFile);
            } else {
                fputs(line, tempFile);
            }
        } else {
            // Handle improperly formatted lines here
            fprintf(stderr, "Error: Malformed line in the file\n");
        }
    }

    fclose(file);
    fclose(tempFile);

    // Replace the original file with the temporary file
    remove(filePath);
    rename(newFilePath, filePath);
}

/**
 * @brief Function to get all clients from a file.
 * @param filepath Path to the file.
 * @param numClients Number of clients in the file.
 * @return Pointer to an array of Client structures.
 */
Client *getAllClients(char *filepath, int numClients) {
    FILE *file = fopen(filepath, "r");
    if (!file) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    char line[MAX_LINE_LENGTH];
    // Skip header line
    if (fgets(line, MAX_LINE_LENGTH, file) == NULL) {
        perror("Error reading file");
        exit(EXIT_FAILURE);
    }

    Client *clients = malloc(numClients * sizeof(Client));
    if (!clients) {
        perror("Memory allocation error");
        exit(EXIT_FAILURE);
    }

    int i = 0;
    while (fgets(line, MAX_LINE_LENGTH, file) != NULL) {
        sscanf(line, "%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,]",
               &clients[i].id, clients[i].service_type, clients[i].first_name, clients[i].last_name,
               clients[i].address, &clients[i].age, clients[i].sex, clients[i].illness,
               &clients[i].room_number, clients[i].specialty, clients[i].doctor,
               clients[i].date, clients[i].time, &clients[i].nights, clients[i].service);
        i++;
    }

    fclose(file);
    return clients;
}

/**
 * @brief Function to search for a client by ID.
 * @param targetID ID to search for.
 * @param filepath Path to the file.
 * @return The client with the specified ID.
 */
Client searchByID(int targetID, char filepath[]) {
    char line[MAX_LINE_LENGTH];
    Client client;
    FILE *fpt;
    fpt = fopen(filepath, "r");

    if (fpt == NULL) {
        perror("Error opening file");
        exit(-1);
    }

    // Read and discard the first line (headers)
    fgets(line, MAX_LINE_LENGTH, fpt);

    // Read and search each line for the target ID
    while (fgets(line, MAX_LINE_LENGTH, fpt) != NULL) {
        processCSVLine(line, &client);
        if (client.id == targetID) {
            return client;
        }
    }

    printf("Client with ID %d not found.\n", targetID);
    fclose(fpt);
}
// Function to search for a client by last name
/**
 * @brief Function to search for a client by last name.
 * @param targetLastName Last name to search for.
 * @param filepath Path to the file.
 * @return The client with the specified last name.
 */
Client searchByLastName(char *targetLastName, char filepath[]) {
    char line[MAX_LINE_LENGTH];
    Client client;
    FILE *fpt;
    fpt = fopen(filepath, "r");

    if (fpt == NULL) {
        perror("Error opening file");
        exit(-1);
    }
    // Read and discard the first line (headers)
    fgets(line, MAX_LINE_LENGTH, fpt);

    // Read and search each line for the target last name
    while (fgets(line, MAX_LINE_LENGTH, fpt) != NULL) {
        processCSVLine(line, &client);
        if (strcmp(client.last_name, targetLastName) == 0) {
            fclose(fpt);
            return client;
        }
    }

    printf("Client with last name %s not found.\n", targetLastName);
    fclose(fpt);
}

/**
 * @brief Comparison function for sorting clients by last name.
 * @param a First client.
 * @param b Second client.
 * @return Negative if a should be before b, positive if a should be after b, 0 if equal.
 */
int compareClientsByName(const void *a, const void *b) {
    return strcmp(((Client *)a)->last_name, ((Client *)b)->last_name);
}

/**
 * @brief Function to sort clients by last name.
 * @param filepath Path to the file.
 * @return Pointer to an array of sorted Client structures.
 */
Client *sortClientsByName(char *filepath) {
    int numClients = countNewlines(filepath);
    Client *clients = getAllClients(filepath, numClients);
    qsort(clients, numClients, sizeof(Client), compareClientsByName);
    return clients;
}

/**
 * @brief Function to filter clients by service type.
 * @param filepath Path to the file.
 * @param serviceType Service type to filter by.
 * @param filteredCount Pointer to store the number of filtered clients.
 * @return Pointer to an array of filtered Client structures.
 */
Client *filterClientsByServiceType(char *filepath, char *serviceType, int *filteredCount) {
    int numClients = countNewlines(filepath);
    Client *clients = getAllClients(filepath, numClients);
    Client *filteredClients = malloc(numClients * sizeof(Client));

    if (!filteredClients) {
        perror("Memory allocation error");
        exit(EXIT_FAILURE);
    }

    *filteredCount = 0;
    for (int i = 0; i < numClients; i++) {
        if (strcmp(clients[i].service_type, serviceType) == 0) {
            memcpy(&filteredClients[*filteredCount], &clients[i], sizeof(Client));
            (*filteredCount)++;
        }
    }

    return filteredClients;
}

/**
 * @brief Function to calculate the bill for a client.
 * @param id ID of the client.
 * @param filepath Path to the file.
 * @return The calculated bill for the client.
 */
int countBill(int id, char *filepath) {
    Client client = searchByID(id, filepath);
    int bill = 0;
    Price servicePrices;
    servicePrices.childbirth_price = 2600;
    servicePrices.health_check_up_price = 50;
    servicePrices.carpal_tunnel_operation = 1250;
    servicePrices.ent_price = 35;
    servicePrices.ultrasound_price = 85;
    servicePrices.colonoscopy = 190;
    servicePrices.mri_price = 400;
    servicePrices.room_price = 68;

    char *service = removeNewlines(client.service);
    if (strcmp(service, "Childbirth") == 0) {
        bill += servicePrices.childbirth_price;
    } else if (strcmp(service, "Health check-up") == 0) {
        bill += servicePrices.health_check_up_price;
    } else if (strcmp(service, "Carpal tunnel operation") == 0) {
        bill += servicePrices.carpal_tunnel_operation;
    } else if (strcmp(service, "ENT") == 0) {
        bill += servicePrices.ent_price;
    } else if (strcmp(service, "Ultrasound") == 0) {
        bill += servicePrices.ultrasound_price;
    } else if (strcmp(service, "Colonoscopy") == 0) {
        bill += servicePrices.colonoscopy;
    } else if (strcmp(service, "MRI") == 0) {
        bill += servicePrices.mri_price;
    }
    free(service);
    bill += client.nights * servicePrices.room_price;
    return bill;
}
