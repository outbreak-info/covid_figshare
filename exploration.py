# Series of functions used in conjunction with parser.py to make sure i'm sucking up all the useful data
# md is the untransformed, raw records from all the API calls.

# All fields within the API
keys = [x.keys() for x in md]

unique(flattenList(keys))

def flattenList(l):
    return([item for sublist in l for item in sublist])


# Looking at custom fields-- stuff was added in by particular instance of the repo.
# NIH version has more funding data
custom = flattenList([x["custom_fields"] for x in md if len(x["custom_fields"])])
# NIH: 12111570
unique([x["name"] for x in custom])


       # *'DOI(s) of associated publication(s):',
       # *'Is this associated with a publication?',
       # ?'Lead author institution',
       # *'Published in',
       # *'Select an IC:',
       # ?"Submitting Author's Institution",

# array(['Acceptance date', 'Administrator link', 'Advisor',
#        'Alternative title', 'Article number', 'Associated authors',
#        'Author affiliation', 'Available date', 'Book series', 'Chair',
#        'Citation', 'Committee Member', 'Contact', 'Copyright date',
#        'Corresponding author email', 'Crick news story', 'DOI',
#        'DOI(s) of associated publication(s):',
#        'Date of in-principle acceptance',
#        'Declaration of conflicts of interest', 'Degree Grantor',
#        'Degree Level', 'Degree name', 'Department', 'Depositor',
#        'Editor(s)', 'Editors', 'Email Address of Submitting Author',
#        'Ethics statement', 'Event dates', 'Human Participants',
#        'I confirm there is no human identifiable information in this dataset.',
#        'ISBN', 'ISSN', 'Illustrator(s)',
#        'Is this associated with a publication?', 'Issue', 'Issue date',
#        'Language', 'Lead author country', 'Lead author institution',
#        'Lead author job role', 'Location', 'Notes',
#        'ORCID of Submitting Author', 'Other identifier', 'Pages',
#        'Pagination', 'Preregistration detail', 'Publication date',
#        'Published in', 'Publisher', 'Publisher DOI',
#        'Publisher Statement', 'Publisher statement', 'Publisher version',
#        'Read full text',
#        'Related publications (DOI or link to DTU Orbit, DTU Findit)',
#        'Research Data Support', 'Research Unit', 'Rights holder',
#        'School', 'Select an IC:', 'Source', 'Spatial coverage',
#        'Submitted date', "Submitting Author's Country",
#        "Submitting Author's Institution", 'Temporal coverage: end',
#        'Temporal coverage: end date', 'Temporal coverage: start',
#        'Temporal coverage: start date', 'Thesis type', 'Version',
#        'Volume', 'eISSN', 'eissn', 'isbn', 'issn'], dtype='<U69')
#
