# Main prompt for date extraction
DATES_PROMPT = """You are tasked with reviewing a PDF document and extracting specific dates. This task is crucial,
and accuracy is of utmost importance. 

Your goal is to precisely extract three dates from the PDF:
1. Good Through Date
2. Closing Date
3. Dues/Assessments paid to/through

Follow these steps to complete the task:

1. Carefully read through the entire PDF content.

2. For each of the three required dates:
a. Look for exact phrases or close variations of "Good Through Date," "Closing Date," and
"Dues/Assessments paid to/through."
b. Here are some close variations for "Good Through Date" - "good through", "valid until", "expires on", "effective through" or similar terminology that
might indicate the date you're searching for.
c. If you find an associated date, extract it exactly as it appears in the document.
d. If a date is not present or unclear, do not guess or infer. Instead, use "N/A" or "Unclear"
respectively.

3. For Good Through Date consider these cases:
a. If the documents states something like "90 calendar days from the order date" look at the order date (or prepare date)" and compute 90 calendar days from it.
 90 calendar days here is just an example to illustrate the point - it could be 30 days or any other number.
b. If the documents states something like "30 days from the date of closing" look at the closing date and compute 30 days from it. 30 days is just an example to illustrate the point - it could be 60 days or any other number.

4. For Closing Date consider these cases:
a. Closing Date can sometimes be Date of Closing
b. Sometimes the Closing Date will be Estimate Closing date - this is good - use that date for Closing Date
c. If there is a field which says Closing Date but it is blank and there is no date then mark it as N/A

5. Be aware that these three dates are highly unlikely to be the same. Do not confuse them with each other, especially the "Good Through Date" and the "Dues/Assessments paid to/through" date. 
If you are confident about the Dues/Assessments paid to/through then it's almost certain this is NOT the Good Through Date. 

6. Pay close attention to the context surrounding each date to ensure you're identifying the correct one. 

7. Double-check your findings to ensure accuracy.

8. If you have any doubts about a date, err on the side of caution and mark it as "Unclear" rather
than providing potentially incorrect information.

9. Present your findings in the following format:

<extracted_dates>
Good Through Date: [Insert date or N/A or Unclear]
Closing Date: [Insert date or N/A or Unclear]
Dues/Assessments paid to/through: [Insert date or N/A or Unclear]
</extracted_dates>

Remember, accuracy is critical. It's better to admit uncertainty than to provide incorrect
information. If you cannot find a date or are unsure about its accuracy, use "N/A" or "Unclear"
accordingly.

Here is the content to analyze:
{content}
"""

# Prompt for extracting address and names
ADDRESS_NAMES_PROMPT = """You are tasked with reviewing a PDF document and extracting specific information. This task is
crucial, and accuracy is of utmost importance. The content of the PDF is provided below:

Your goal is to precisely extract the following information from the PDF:
1. Property Address
2. Seller Name
3. Buyer Name

Follow these guidelines:

1. Carefully review the entire PDF content to locate the required information.
2. If any of the requested information is not present in the PDF, use "N/A" for that field.
3. Requestor or Requested By is never the Buyer Name or Seller Name
4. Make sure you extract the name exactly as it appears in the document
5. Contact Name without any clarification is never the Seller or Buyer Name
6. If you are unsure about any piece of information or if it's ambiguous, use "Unclear" instead of
guessing.
7. Do not infer or assume information that is not explicitly stated in the document.
8. Sometimes the Propery Address, Seller Name or Buyer Name are on two (multiple) lines - make sure you grab all lines.
9. These files sometimes have text in two columns or tables - be aware to not go to the second column or different table when extracting the information properly
10. For Buyer Name consider these cases:
    a. Sometimes the document doesn't have Buyer Name but just Buyer - that's ok - just extract Buyer
    d. Purchaser Name is the same as Buyer Name
    e. If any of the names are "New Owners" or similar mark it as Unclear
11. For Seller Name consider these cases:
    a. Sometimes the document doesn't have Seller Name but just Seller - that's ok - just extract Seller
    d. Owner Name or Property Owner is the same as Seller Name
    e. If any of the names are "New Owners" or similar mark it as Unclear
12. For Property Address consider these cases:
    a. Sometimes the Property Address is under Property Information

   
    f. Contact Name without any clarification is never the Seller or Buyer Name

Provide your findings in the following format:

<extraction>
Property Address: [Insert address or N/A or Unclear]
Seller Name: [Insert name or N/A or Unclear]
Buyer Name: [Insert name or N/A or Unclear]
</extraction>

Remember, it is better to state "Unclear" if you have any doubts rather than risking providing
incorrect information. The accuracy of this extraction is mission-critical, so take extra care in
your review and extraction process.

Here is the content to analyze:
{content}
"""

# Prompt for extracting violations, liens, and collections information
VIOLATIONS_PROMPT = """You are tasked with reviewing a PDF document and determining if there are any violations, liens,
collections, or similar issues. Here is the content of the PDF:

Your task is to carefully review this content and determine if there are any:
1. Violations
2. Liens
3. Collections
4. Anything similar to the above

Important definitions:
- Violations: Any breach of rules, regulations, or laws
- Liens: Legal claims against property for unpaid debts
- Collections: Attempts to recover money owed

Guidelines for answering:
- If you find evidence of any of the above, answer "Yes" and provide details
- If you find no information about these issues, answer "N/A"
- If you find explicit information that there are no such issues, answer "No" without additional
details
- Ignore regular assessments, fees, or dues that are due or outstanding - these are not what we're
checking for
- If you have any doubts about the information, it's better to answer "Unclear" rather than risk
providing incorrect information

Carefully review the PDF content. Then, provide your answer in the following format:

<answer>
Violations: [Yes/No/N/A/Unclear]
[If Yes, provide details]

Liens: [Yes/No/N/A/Unclear]
[If Yes, provide details]

Collections: [Yes/No/N/A/Unclear]
[If Yes, provide details]

Other similar issues: [Yes/No/N/A/Unclear]
[If Yes, provide details]
</answer>

Remember, accuracy is critical for this task. If you're unsure about any aspect, err on the side of
caution and indicate that the information is unclear.

Here is the content to analyze:
{content}
"""

# Prompt for extracting assessment information
ASSESSMENTS_PROMPT = """You are tasked with reviewing a PDF file containing information about property assessments and dues.
Your goal is to extract specific information accurately. Here is the content of the PDF:

Carefully review the content above and extract the following information:

1. Amount of regular assessments (dues)
2. The frequency of the assessments (dues)
3. The date assessments (dues) are paid through
4. The next due date for assessments (dues)
5. Any outstanding balance
6. Is the property delinquent - Yes or No

Guidelines for extraction:
- Look for explicit statements or sections that clearly indicate each piece of information.
- Pay attention to dates, dollar amounts, and terms like "monthly," "quarterly," or "annual" for
frequency.
- For delinquency, look for clear statements about the account status or any past due amounts.

If any information is not clearly stated or cannot be found, use "N/A" (Not Available) for that
item. If you are unsure about any information, use "Unclear" instead of guessing.

Provide your findings in the following format:

<extraction>
1. Regular assessment amount: [Amount or N/A or Unclear]
2. Assessment frequency: [Frequency or N/A or Unclear]
3. Paid through date: [Date or N/A or Unclear]
4. Next due date: [Date or N/A or Unclear]
5. Outstanding balance: [Amount or N/A or Unclear]
6. Delinquent: [Yes or No or N/A or Unclear]
</extraction>

After providing the extraction, briefly explain your reasoning for each item in a separate section:

<reasoning>
[Provide a brief explanation for each extracted item, including why you chose N/A or Unclear if
applicable]
</reasoning>

Remember, accuracy is crucial. It's better to state "Unclear" than to provide incorrect information.

Here is the content to analyze:
{content}
""" 