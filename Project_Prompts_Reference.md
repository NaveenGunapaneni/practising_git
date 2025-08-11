# Project Prompts Reference
## Complete Collection of Development Prompts for Future Projects

**Document Version:** 1.0  
**Date:** August 2025  
**Project:** GeoPulse Web Application  
**Purpose:** Reference for future project development  

---

## Table of Contents
1. [Business Requirements Document (BRD)](#business-requirements-document-brd)
2. [Low-Level Design Documents](#low-level-design-documents)
3. [API Technical Specifications](#api-technical-specifications)
4. [UI Technical Documentation](#ui-technical-documentation)
5. [DBA Activities & Operations](#dba-activities--operations)
6. [Testing Documentation](#testing-documentation)
7. [Developer Mindset Guides](#developer-mindset-guides)

---

## Business Requirements Document (BRD)

### **Original Prompt:**
```
write BRD document and store in "requirement" folder.
```

### **Context:** 
Initial request to create a comprehensive Business Requirements Document for the GeoPulse Web Application.

### **Deliverable:** 
`requirements/BRD_GeoPulse_WebApplication.md`

---

## Low-Level Design Documents

### **Original Prompt:**
```
create low level desing document which is very detailed sothat developer can start creating the code. create the documets in corresponding UI,Testing, API,Database folders. for testing, give user test cases with expected resutls for all the application with track of funcitonal cases. keep in mind, my developers are just out of college. Need very detail instructions.
```

### **Follow-up Clarification:**
```
already these folders are existing in "design". use them.
```

### **Context:** 
Request for detailed low-level design documents that would enable new college graduates to start coding immediately, with specific focus on comprehensive testing documentation.

### **Deliverables:** 
- `design/UI/UI_Low_Level_Design.md`
- `design/API/API_Low_Level_Design.md`
- `design/Database/Database_Low_Level_Design.md`
- `design/Testing/Testing_Low_Level_Design.md`

---

## API Technical Specifications

### **Original Prompt:**
```
For API create "Technical Specification Document": create one each document for each APIs mentioned. in API folder. each API give separate document with propert specs 1. input json 2. out json 3. processing required in plain english 4. logging, security, exception hadling etc requred 5. database details and connectivity information 6. postman what to enter and how to test.
```

### **Context:** 
Request for detailed technical specifications for each API endpoint, including input/output formats, processing logic, security measures, and testing instructions.

### **Deliverables:** 
- `design/API/API-1_User_Registration_Specification.md`
- `design/API/API-2_User_Authentication_Specification.md`
- `design/API/API-3_Dashboard_Data_Specification.md`
- `design/API/API-4_File_Upload_Processing_Specification.md`

---

## UI Technical Documentation

### **Original Prompt:**
```
For UI Give Technical documentation with follwoing information. create one each docuemnt for each UI specication 1. wireframe diagrams 2. sample test API. how to create test API directions. 3. testing tips for UI 4. styling tips about approrpiatee UX
```

### **Context:** 
Request for comprehensive UI technical documentation including wireframes, test API setup instructions, testing guidance, and UX styling recommendations.

### **Deliverables:** 
- `design/UI/UI-1_Login_Page_Technical_Documentation.md`
- `design/UI/UI-2_Dashboard_Page_Technical_Documentation.md`
- `design/UI/UI-3_File_Upload_Page_Technical_Documentation.md`

---

## DBA Activities & Operations

### **Original Prompt:**
```
For Database:
create a file for DBA activitis required like backup, recovery, moving data from one server to other, restricting connections to server. protecting the database from outside calls.
```

### **Context:** 
Request for comprehensive DBA operations guide covering backup, recovery, data migration, connection management, and security measures.

### **Deliverable:** 
`design/Database/DBA_Activities_Operations_Guide.md`

---

## Testing Documentation

### **Original Prompt:**
```
For Testing:
create excel sheets with detailed test cases for all functional areas.
he should assure UI, API, DB are functional, meeting user needs, very secured from outside world.
```

### **Context:** 
Request for comprehensive test case documentation in Excel format covering all functional areas with focus on security and user needs validation.

### **Deliverables:** 
- `design/Testing/Test_Cases_UI_Functional.csv`
- `design/Testing/Test_Cases_API_Functional.csv`
- `design/Testing/Test_Cases_Database_Functional.csv`

### **Follow-up Issue Resolution:**
```
test cases files created are not getting opened.
fix the problem or create the files in csv.
error:
Excel cannot open the file 'Test_Cases_UI_Functional.xlsx' because the file format or file extension is not valid. Verify that the file has not been corrupted and that the file extension matches the format of the file.
```

### **Context:** 
Issue with Excel file format - resolved by creating proper CSV files that can be opened in Excel.

---

## Developer Mindset Guides

### **API Developer Mindset Prompt:**
```
API developer is little rigit and has "Analysis Paralalysis".
give tips about the how the API developer should think.
how he has to overcome his problems.
```

### **Context:** 
Request for guidance to help API developers overcome analysis paralysis and develop effective mindset for building robust APIs.

### **Deliverable:** 
`design/API/API_Developer_Mindset_Guide.md`

### **DBA Completion Mindset Prompt:**
```
Database guy:
he always says its over, even not completing the 10% of work.
He has problem with definition of completion.
give tips and tricks for DBA .
```

### **Context:** 
Request for guidance to help DBAs overcome "It's Done" syndrome and develop clear definitions of completion for database work.

### **Deliverable:** 
`design/Database/DBA_Completion_Mindset_Guide.md`

### **UI/UX Designer Mindset Prompt:**
```
For UI/UX designer:
give tips and tricks for how the thought process of UI/UX developer should be.
tools around to use for giving better UI/UX
```

### **Context:** 
Request for comprehensive guide covering UI/UX designer thought processes, design methodologies, and essential tools for creating better user experiences.

### **Deliverable:** 
`design/UI/UI_UX_Designer_Mindset_Guide.md`

---

## Tester Mindset Guide

### **Original Prompt:**
```
for tester:
give tips how his attitude whle testing.
give tips on probing and detective for loophole
```

### **Context:** 
Request for guidance on testing mindset, attitude, and detective techniques for finding bugs and loopholes in applications.

### **Deliverable:** 
`design/Testing/Tester_Mindset_Detective_Guide.md`

---

## Detailed Project Planning

### **Original Prompt:**
```
with all components, give detailed project plan.
include tasks like 
1. checkin the code to git
2. get the peer review on code
3. update the project plan and report any deviation.
4. give tasks for integrations.

give appropriate dates to get this completed by 14th of August.
take care of dependencies of each tasks.
```

### **Context:** 
Request for comprehensive project planning with code management, peer review, project tracking, and integration tasks, with specific completion date and dependency management.

### **Deliverable:** 
`Project_Plan_Detailed.md`

---

## Complete File Structure Created

### **Requirements:**
```
requirements/
├── BRD_GeoPulse_WebApplication.md
```

### **Design Documentation:**
```
design/
├── UI/
│   ├── UI_Low_Level_Design.md
│   ├── UI-1_Login_Page_Technical_Documentation.md
│   ├── UI-2_Dashboard_Page_Technical_Documentation.md
│   ├── UI-3_File_Upload_Page_Technical_Documentation.md
│   └── UI_UX_Designer_Mindset_Guide.md
├── API/
│   ├── API_Low_Level_Design.md
│   ├── API-1_User_Registration_Specification.md
│   ├── API-2_User_Authentication_Specification.md
│   ├── API-3_Dashboard_Data_Specification.md
│   ├── API-4_File_Upload_Processing_Specification.md
│   └── API_Developer_Mindset_Guide.md
├── Database/
│   ├── Database_Low_Level_Design.md
│   ├── DBA_Activities_Operations_Guide.md
│   └── DBA_Completion_Mindset_Guide.md
└── Testing/
    ├── Testing_Low_Level_Design.md
    ├── Tester_Mindset_Detective_Guide.md
    ├── Test_Cases_UI_Functional.csv
    ├── Test_Cases_API_Functional.csv
    └── Test_Cases_Database_Functional.csv
```

### **Project Planning:**
```
Project_Plan_Detailed.md
```

---

## Key Themes Across All Prompts

### **1. Comprehensive Documentation**
- All prompts requested detailed, comprehensive documentation
- Focus on enabling new developers to start working immediately
- Emphasis on step-by-step instructions and examples

### **2. Developer-Focused Approach**
- Multiple prompts specifically mentioned "college graduates" or "new developers"
- Need for very detailed instructions and explanations
- Focus on practical, actionable guidance

### **3. Security and Quality**
- Consistent emphasis on security measures
- Focus on testing and validation
- Quality assurance and best practices

### **4. Mindset and Process**
- Several prompts focused on developer mindset and attitude
- Emphasis on overcoming common development challenges
- Process improvement and workflow optimization

### **5. Tool and Technology Guidance**
- Specific requests for tool recommendations
- Technology stack guidance
- Best practices for modern development

---

## Reusable Prompt Templates

### **For Business Requirements:**
```
write BRD document and store in "requirement" folder.
```

### **For Low-Level Design:**
```
create low level design document which is very detailed so that developer can start creating the code. create the documents in corresponding [UI/Testing/API/Database] folders. for [specific area], give [specific requirements]. keep in mind, my developers are just out of college. Need very detail instructions.
```

### **For Technical Specifications:**
```
For [component] create "Technical Specification Document": create one each document for each [component] mentioned. in [folder] folder. each [component] give separate document with proper specs 1. [specification 1] 2. [specification 2] 3. [specification 3] 4. [specification 4] 5. [specification 5] 6. [specification 6].
```

### **For Testing Documentation:**
```
For Testing: create excel sheets with detailed test cases for all functional areas. ensure [component 1], [component 2], [component 3] are functional, meeting user needs, very secured from outside world.
```

### **For Mindset Guides:**
```
For [role]: give tips and tricks for how the thought process of [role] should be. [specific focus area] for giving better [output].
```

### **For Problem-Solving Guides:**
```
[Role] has [specific problem]. give tips about how the [role] should think. how he has to overcome his problems.
```

### **For Detailed Project Planning:**
```
with all components, give detailed project plan.
include tasks like 
1. checkin the code to git
2. get the peer review on code
3. update the project plan and report any deviation.
4. give tasks for integrations.

give appropriate dates to get this completed by [target_date].
take care of dependencies of each tasks.
```

---

## Lessons Learned

### **1. Prompt Clarity**
- Be specific about deliverables and format
- Mention target audience (e.g., "college graduates")
- Specify folder structure and organization

### **2. File Format Considerations**
- Consider compatibility issues (Excel vs CSV)
- Test file formats before delivery
- Provide alternative formats when needed

### **3. Comprehensive Coverage**
- Cover all aspects: technical, mindset, tools, processes
- Include both high-level strategy and detailed implementation
- Address common pain points and challenges

### **4. Developer Experience**
- Focus on practical, actionable guidance
- Provide step-by-step instructions
- Include examples and templates

### **5. Quality Assurance**
- Emphasize testing and validation
- Include security considerations
- Provide monitoring and maintenance guidance

---

## Future Project Application

### **When Starting a New Project:**
1. **Use the BRD prompt** to establish project requirements
2. **Apply the LLD prompts** for each component area
3. **Use technical specification prompts** for detailed API/UI documentation
4. **Apply testing prompts** for comprehensive test coverage
5. **Use mindset guides** to address team development challenges
6. **Use detailed project planning prompt** for comprehensive timeline and task management

### **Customization Tips:**
- Replace "GeoPulse" with your project name
- Adjust folder structures as needed
- Modify specifications based on your technology stack
- Adapt testing requirements to your specific needs
- Customize mindset guides for your team's challenges

### **Quality Checklist:**
- [ ] All documentation is comprehensive and detailed
- [ ] Instructions are clear for new developers
- [ ] Security considerations are addressed
- [ ] Testing coverage is complete
- [ ] Tools and technologies are specified
- [ ] Mindset and process guidance is included

---

## Summary

This collection of prompts represents a comprehensive approach to project documentation and team development. Each prompt was designed to create detailed, actionable documentation that enables new developers to contribute effectively while maintaining high quality and security standards.

The prompts can be reused and adapted for future projects, providing a solid foundation for:
- Project requirements and planning
- Technical documentation and specifications
- Testing strategies and test cases
- Team development and mindset improvement
- Tool selection and best practices
- Comprehensive project planning and timeline management

Remember to customize these prompts for your specific project needs, technology stack, and team requirements.
