"""
Functions for parsing csv file and emailing users.
"""

# Import modules.
import pandas as pd
from string import Template
import os
import sys
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def parse_csv(csv_path):
    """
    Parse csv of datasets with their associated data maintainers.
    Return a list of python dictionaries with information about dataset.
    """
    try:
        if os.path.exists(csv_path):
            with open(csv_path, "r") as csv_file:
                # Read data from csv as dataframe.
                data = pd.read_csv(csv_file)
                # Filter out records with NA values.
                data = data.dropna()
                # Filter out records where update frequency is 'Not Planned' or 'As Needed'
                data = data[~data["update_frequency"].isin(["Not Planned", "As Needed"])]
                # Filter out records where last modified date was over 365 days ago.
                data = data[data["days_since_modified"] >= 365]
                # Remove records where resource is a document or zip file.
                data = data[~data["name"].str.contains(".pdf|.docx|.doc|.zip")]
                # Group data and aggregate unique values from other columns into lists.
                data_grouped = data.groupby(["title", "maintainer_email", "maintainer_name", "url"],
                                            as_index=False)["name", "days_since_modified"].agg(lambda x: list(x))
                # Convert grouped data to dictionary.
                data_dict = data_grouped.to_dict('r')
                return data_dict
    except Exception as e:
        print(e.args)


def read_templates(body_file, subject_file):
    """
    Open email message and subject templates and return Template objects made from their contents.
    """
    try:
        with io.open(body_file, "r", encoding="utf-8") as msg_template:
            msg_template_content = msg_template.read()
        with io.open(subject_file, "r", encoding="utf-8") as subject_template:
            subject_template_content = subject_template.read()
        return Template(msg_template_content), Template(subject_template_content)
    except Exception as e:
        print(e.args)


def setup_smtp(dataset_records, message_template, subject_template):
    """
    Establishes connection with MailGun server. Loops through data in list of dictionaries from
    SQL database query. For each record, send an email to the data maintainer with details about the
    dataset they are responsible for.
    """
    try:
        if dataset_records is None:
            # If dataset records is None, exit program.
            sys.exit()
        else:
            # Set up the SMTP server with mailgun settings.
            server = smtplib.SMTP(host=os.environ.get("CKAN_SMTP_SERVER"))

            # Start connection to server and login with credentials.
            server.starttls()
            server.login(os.environ.get("CKAN_SMTP_USER"), os.environ.get("CKAN_SMTP_PASSWORD"))

            # For each record (dataset) in csv, send message.
            for record in dataset_records:
                msg = MIMEMultipart()

                # Add in the actual person name to the message template.
                message = message_template.substitute(PERSON_NAME=record.get("maintainer_name"),
                                                      DATASET_NAME=record.get("title"),
                                                      DAYS_SINCE_MODIFIED_MAX=max(record.get("days_since_modified")),
                                                      DATA_URL=record.get("url"))

                # Add in custom subject with dataset name.
                subject = subject_template.substitute(DATASET_NAME=record.get("title"))

                # Setup the parameters of the message.
                msg["From"] = os.environ.get("CKAN_SMTP_MAIL_FROM")
                msg["To"] = record["maintainer_email"]
                msg["Subject"] = subject

                # Add the message from template to body of email.
                msg.attach(MIMEText(message, "plain"))

                # Send the message via the server set up earlier.
                server.sendmail(msg["From"], msg["To"], msg.as_string())

            server.quit()
    except Exception as e:
        print(e.args, e.message)
    del msg


def main():
    # Load data from csv file - results from SQL query to extract dataset maintainer details.
    maintainer_list = parse_csv("/tmp/maintainer_details.csv")

    # Load template email body and subject.
    email_template_obj = read_templates("templates/emails/data_maintainer.txt",
                                        "templates/emails/data_maintainer_subject.txt")

    # Use data from maintainer_list and email_template_obj to send email to list of users.
    setup_smtp(maintainer_list, email_template_obj[0], email_template_obj[1])


if __name__ == "__main__":
    main()
