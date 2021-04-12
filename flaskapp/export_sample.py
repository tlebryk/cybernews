from exportword import export_doc

b1 = '''The Biden administration is escalating efforts to safeguard the U.S. power grid from hackers, developing a plan to better coordinate with industry to counter threats and respond to cyber attacks, according to people familiar with the matter.

Top administration officials, including Energy Secretary Jennifer Granholm and Deputy National Security Adviser Anne Neuberger, briefed top utility industry executives on the efforts in a March 16 meeting, said the people, who requested anonymity because the session was private.

The plan, which could prompt widespread changes in standards and cyber defense strategies, is set to be issued within weeks. U.S. officials hope to create plans for other critical industries but are starting with the electrical sector because of its importance to the economy and recent activities targeting the grid by foreign hackers, one person said.

The high-level meeting indicated the seriousness of the initiative, which is meant to knit together the full force of the government, in alignment with the private sector, to confront increasingly aggressive actions by U.S. adversaries to target the electrical grid.

Those acts include inserting malicious software that could be activated to disrupt electricity generation or distribution in the U.S. Russia is among the adversaries that have already launched such operations, including a sprawling attack in 2017. But other countries are targeting the grid, including North Korea and Iran, one person familiar with the government’s assessment said.

The issue has gained renewed attention in the wake of a highly sophisticated attack that compromised popular software from Texas-based SolarWinds Corp. The hack, which affected as many as 18,000 SolarWinds customers, has underscored concerns about the vulnerability of the nation’s critical infrastructure amid persistent cyber threats.

The administration plans to produce a so-called operational technology action plan that will begin with the power industry and expand to other critical sectors such as natural gas distribution, chemical refining and municipal water systems, said one person briefed on the plan. Operational technology, also known as OT, includes the specialized controls used to run the nation’s nuclear plants, refineries, pipelines and other infrastructure.

Power industry advances in cybersecurity make the sector a good place to start as officials beef up protections for the nation’s critical infrastructure, another person said.

A National Security Council spokeswoman didn’t immediately comment.

The federal government and utilities have a long history of coordination on cybersecurity, with power companies required to report not just successful breaches of their control systems but attempted intrusions. The sector is a chief target of U.S. foes, with security analysts and utility executives warning of a barrage of constant attempts on the systems.

Companies, however, have long complained that the government hasn’t spoken with one voice about how to address vulnerabilities, and that its recommendations haven’t always been synchronized -- concerns that were raised in this month’s meeting. The National Commission on Grid Resilience last year said the industry still needs more information on threats.

President Joe Biden intends to put the full weight of the government into the effort, with agencies including the State and Energy departments along with the National Security Agency enlisted to harden defenses and respond to breaches. On Sunday, Biden said he was “close” to naming someone to serve as national cyber director, a position created by Congress to coordinate the government’s efforts to combat and retaliate for hacks.

The administration’s plan will include efforts to get greater visibility on private sector risks, and to clarify the role of key agencies, including the Homeland Security and Energy departments. The administration also wants to better plot responses to incidents -- including who’s involved and what resources are deployed after a company is compromised.

Although similar blueprints have been developed in the past, the involvement of top administration officials and their holistic approach is new, according to one person familiar with the matter.

A chief concern is deciding the shape of collective defense and response efforts. Administration officials at the March 16 meeting made clear they were seeking to enhance coordination, communication, reporting and response between the industry and government.

The virtual session was the first broad meeting between top Biden administration officials and executives in the Electricity Subsector Coordinating Council, a group designed to further industry-government coordination on protecting the grid.

The electric power sector values its close working relationship with partners in government, said Scott Aaronson, vice president for security and preparedness at the Edison Electric Institute that represents investor-owned electric companies.

“We appreciate that this administration already is coordinating with grid operators to protect critical energy infrastructure,” Aaronson said in an emailed statement. “Protecting and defending critical infrastructure is a shared responsibility that requires engagement and expertise from asset owners and government partners.”
'''


articles = [
    {
        "url": "https://www.bloomberg.com/news/articles/2021-03-28/biden-team-boosts-effort-to-shield-power-grid-from-cyber-threats?srnd=code-wars",
        "title": "Biden Team Boosts Effort to Shield U.S. Power Grid From Hackers",
        "author": "Jennifer Jacobs, Jennifer A. Dlouhy, and Michael Riley",
        "body":  b1,
        "source": "Bloomberg",
        "date": "March 29, 2021"
    },
        {
        "url": "https://www.bloomberg.com/news/articles/2021-03-28/biden-team-boosts-effort-to-shield-power-grid-from-cyber-threats?srnd=code-wars",
        "title": "SolarWinds hack got emails of top DHS officials",
        "author": "Alan Suuderman",
        "body":  b1,
        "source": "AP News",
        "date": "March 28, 2021"
    },
]

cyber_export(articles, "text.docx")