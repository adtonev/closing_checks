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
VIOLATIONS_PROMPT = """You are a highly experienced Title & Escrow officer working on real estate closings. Your goal is to carefully examine the provided PDF content from a document used for real estate closingsand identify any violations, liens, collections, delinquencies, or similar issues that may affect the property's status. 


Here is the content of the PDF document you need to analyze:

<pdf_content>
{content}
</pdf_content>

Your task is to thoroughly review this content and determine if there are any:
1. Violations
2. Liens
3. Collections
4. Delinquencies
5. Special Assessments
6. Any other similar issues

Important definitions:
- Violations: Any breach of rules, regulations, or laws related to the property
- Liens: Legal claims against the property for unpaid debts
- Collections: Attempts to recover money owed related to the property
- Delinquencies: Overdue payments or unfulfilled financial obligations related to the property
- Special Assessments: Additional fees imposed on property owners for specific improvements or services

Instructions:
1. Carefully read through the entire PDF content.
2. For each category (violations, liens, collections, delinquencies, special assessments, and other similar issues), determine if there is evidence of any issues.
3. Use the following criteria for your answers:
   - Answer "Yes" if you find clear evidence of an issue, and provide specific details.
   - Answer "No" if you find explicit information stating there are no such issues.
   - Answer "N/A" if you find no information about these issues.
   - Answer "Unclear" if the information is ambiguous or you have any doubts, and explain why.
4. Ignore regular assessments, fees, or dues that are due or outstanding - these are not what we're checking for.
5. Accuracy is critical. If you're unsure about any aspect, err on the side of caution and indicate that the information is unclear.
6. You should ignore anything hypothetical and only consider active, known, recorded, definitive, or explicit violations, liens, collections, delinquencies, special assessments, or other issues.
7. You should ignore information that might be in other documents unless these documents are explicitely mentioned as attached to the document you are reviewing.
8. If the document states that there are no active, known, recorded, definitive, explicit violations, liens, collections, delinquencies, or special assessments then ignore disclaimers.
9. If the response in the document field is blank then treat it as No.

Before providing your final extraction, wrap your analysis inside <document_review> tags. In this section:
- List potential indicators or keywords for each category (violations, liens, collections, delinquencies, and other similar issues).
- Quote relevant sections from the PDF content for each category.
- Consider both explicit and implicit evidence for each category.
- Show your thought process and reasoning for each category.

This will help ensure a thorough and accurate review of the document. It's OK for this section to be quite long.

After your analysis, provide your final extraction in the following format:

<extraction>
Violations: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Liens: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Collections: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Delinquencies: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Special Assessments: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Other similar issues: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]
</extraction>

Remember, hyper-accuracy is crucial for this task. Take your time to carefully analyze the document and provide well-reasoned, detailed responses when necessary."""

# Prompt for Gemini 2.5 Pro model - thinking-based approach
VIOLATIONS_PROMPT_THINKING = """You are a highly experienced Title & Escrow officer working on real estate closings. Your goal is to carefully examine the provided PDF content from a document used for real estate closingsand identify any violations, liens, collections, delinquencies, or similar issues that may affect the property's status. 

Here is the content of the document you need to analyze:

<property_document>
{content}
</property_document>

Your primary objective is to thoroughly review this content and determine if there are any:
1. Violations
2. Liens
3. Collections
4. Delinquencies
5. Special Assessments
6. Any other similar issues

Key Definitions:
- Violations: Breaches of rules, regulations, or laws related to the property
- Liens: Legal claims against the property for unpaid debts
- Collections: Attempts to recover money owed related to the property
- Delinquencies: Overdue payments or unfulfilled financial obligations related to the property
- Special Assessments: Fees charged by a governing body for specific improvements or services

Instructions:
1. Read the entire document content carefully.
2. For each category (violations, liens, collections, delinquencies, special assessments, and other similar issues), analyze whether there is evidence of any issues.
3. Use the following criteria for your answers:
   - "Yes" if you find clear evidence of an issue. Provide specific details.
   - "No" if you find explicit information stating there are no such issues.
   - "N/A" if you find no information about these issues.
   - "Unclear" if the information is ambiguous or you have doubts. Explain your reasoning.
4. Disregard regular assessments, fees, or dues that are due or outstanding.
5. Prioritize accuracy. If you're unsure about any aspect, indicate that the information is unclear.
6. You should ignore anything hypothetical and only consider active, known, recorded, definitive, or explicit violations, liens, collections, delinquencies, special assessments, or other issues.
7. You should ignore information that might be in other documents unless these documents are explicitely mentioned as attached to the document you are reviewing.
8. If the document states that there are no active, known, recorded, definitive, explicit violations, liens, collections, delinquencies, or special assessments then ignore disclaimers.
9. If the response in the document field is blank then treat it as No.

Before providing your final extraction, conduct a thorough analysis in <analysis> tags inside your thinking block. In this section:
- List potential indicators or keywords for each category.
- Quote relevant sections from the document content for each category.
- Consider both explicit and implicit evidence.
- Analyze the strength and relevance of each piece of evidence.
- Consider alternative interpretations of the information.
- Express any uncertainties or ambiguities you encounter.
- Show your thought process and reasoning for each category.

After your analysis, provide your final extraction in the following format:

<extraction>
Violations: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Liens: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Collections: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Delinquencies: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Special Assessments: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]

Other similar issues: [Yes/No/N/A/Unclear]
[If Yes or Unclear, provide details and context]
</extraction>

Remember to:
- Take your time to carefully analyze the document.
- Consider multiple perspectives before making a decision.
- Provide well-reasoned, detailed responses when necessary.
- Express uncertainty when appropriate rather than making unfounded claims.

Your thorough and accurate analysis is crucial for making informed decisions about the property's status.

Your final output should consist only of the extraction and should not duplicate or rehash any of the work you did in the analysis section."""

# Prompt for extracting assessment information
ASSESSMENTS_PROMPT = """You are a highly experienced Title & Escrow officer working on real estate closings. You are specializing in extracting specific financial information from real estate documents. Your task is to analyze the following PDF content and extract key details about regular assessments (dues).

Here is the content of the PDF to analyze:

<pdf_content>
{{PDF_CONTENT}}
</pdf_content>

Your goal is to extract the following information:
1. Amount of regular assessments (dues)
2. The frequency of the assessments (dues)
3. Any outstanding balance

Important Guidelines:
- Focus only on regular assessments (dues). Ignore transfer, move-in, move-out, or additional closing fees.
- Extract precise numbers without additional text.
- The assessment amount might be the sum of all recurring service fees.
- "Property Assessment" may be synonymous with "Assessment (Dues)".
- Prioritize current numbers over past ones if there's a contradiction.
- Look for an "Assessment Data" section for relevant information.
- Simplify frequency terms (e.g., "per Month" to "Monthly", "per Year" to "Annually").
- Don't infer information; use only directly mentioned data.
- If all recurring fees have the same frequency, use that frequency.

Process:
1. Carefully read through the PDF content.
2. Write your analysis inside <detailed_breakdown> tags:
   - Quote relevant sections from the PDF content for each piece of information we're looking for.
   - List out all recurring fees you find, with their amounts and frequencies.
   - Identify relevant sections or statements related to each piece of information.
   - Explain how you determined each value or why you couldn't find it.
   - Show any calculations or reasoning used to arrive at your conclusions, including summing up fees or converting frequencies.
3. Provide your final extraction in <extraction> tags.
4. Summarize your reasoning for each extracted item in <reasoning> tags.

Use "N/A" (Not Available) if information is not clearly stated or cannot be found. Use "Unclear" if you are unsure about any information.

Example output structure:

<detailed_breakdown>
[Your detailed analysis of the PDF content, showing your thought process for each item]
</detailed_breakdown>

<extraction>
1. Regular assessment amount: [Amount or N/A or Unclear]
2. Assessment frequency: [Frequency or N/A or Unclear]
3. Outstanding balance: [Amount or N/A or Unclear]
</extraction>

<reasoning>
[Brief explanation for each extracted item, including why you chose N/A or Unclear if applicable]
</reasoning>

Remember, accuracy is crucial. It's better to state "Unclear" than to provide incorrect information. Please proceed with your analysis and extraction based on the provided PDF content.
"""

# Prompt for analyzing document attachments
ATTACHMENTS_PROMPT = """You are tasked with reviewing a PDF document to determine if there is any mention of attachments or
attached documents. This task is mission critical, so accuracy is of utmost importance. Please
follow these instructions carefully:

1. Carefully read through the following PDF content:

<pdf_content>
{content}
</pdf_content>

2. As you review the content, pay close attention to any words or phrases that might indicate the
presence of attachments or additional documents. Look for keywords such as:
- "attachment"
- "attached"
- "enclosed"
- "appended"
- "accompanying document"
- "see attached"
- "please find attached"

3. After your thorough review, provide your answer in the following format:

<answer>
[Your response here]
</answer>

4. Your response should be one of two options:
a. If there is no mention of attachments or attached documents, simply write:
No

b. If there is mention of attachments or attached documents, write:
Yes, [name of the attached document(s)]

5. Remember, this task is mission critical. Double-check your answer before providing it. Make sure
you have not missed any mentions of attachments, no matter how subtle they might be.

6. Do not include any additional explanations or justifications in your answer. Stick strictly to
the format provided in step 4."""

# Prompt for identifying additional associations and districts
EXTRA_ASSOCIATIONS_PROMPT = """You are tasked with reviewing a PDF document to identify any mentions of additional homeowners
associations or special districts. This task is critically important and requires careful attention
to detail.

First, you will be provided with the content of the PDF document:

<pdf_content>
{content}
</pdf_content>

Carefully read and analyze the entire content of the PDF. Pay close attention to any mentions of:

1. Homeowners associations (HOAs), including:
- Sub associations
- Master associations
- Any other type of association related to property management

2. Special districts, such as:
- Metro districts
- Water districts
- Fire districts
- Any other type of special district

After your analysis, provide your answer in the following format:

1. If there are no mentions of additional homeowners associations or special districts:
<answer>No</answer>

2. If there are mentions of additional entities:
<answer>Yes, [Name of Entity 1], [Name of Entity 2], ...</answer>

List all relevant entities found, separated by commas.

Remember, accuracy is crucial for this task. Double-check your findings before providing your
answer.

Examples of correct responses:
1. <answer>No</answer>
2. <answer>Yes, Lakeside Master Association, Cherry Creek Water District</answer>
3. <answer>Yes, Pinecrest Sub Association</answer>

Ensure that your response is precise and based solely on the information provided in the PDF
content. Do not make assumptions or include information not explicitly mentioned in the document."""