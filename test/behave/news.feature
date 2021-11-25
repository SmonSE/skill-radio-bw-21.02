Feature: mycroft-radio

  Background:
    Given an english speaking user

  Scenario Outline: what's the radio
    Given nothing is playing
    When the user says "<what's the radio>"
    Then "mycroft-radio" should reply with dialog from "radio.dialog"

   Examples: What's the radio - standard intent
     | what's the radio |
     | radio |
     | brief me |
     | other radio |
     | what's new |
     | radio briefing |
     | breaking radio |
     | what's the radio |
     | let's hear the radio |
     | what's the latest radio |
     | what's today's briefing |
     | what's the breaking radio |
     | give me the radio updates |
     | tell me what's happening |
     | brief me on the headlines |

  Scenario Outline: Play the radio using Common Play Framework
    Given nothing is playing
    When the user says "<play the radio>"
    Then "mycroft-playback-control" should reply with dialog from "radio.dialog"

   Examples: play the radio
     | play the radio |
     | play the radio |
     | play radio |
     | play radio briefing |
     | play headlines |
     | play the latest radio |
     | play today's radio |
     | play today's headlines |
     | play the radio again |

  Scenario Outline: stop radio playback
    Given radio is playing
    When the user says "<stop the radio>"
    Then "mycroft-radio" should stop playing

   Examples: stop radio playback
     | stop the radio |
     | stop |
     | stop playing |

  @xfail
  # Jira MS-108 https://mycroft.atlassian.net/browse/MS-108
  Scenario Outline: Failing stop radio playback
    Given radio is playing
    When the user says "<stop the radio>"
    Then "mycroft-radio" should stop playing

   Examples: stop radio playback
     | stop the radio |
     | quit |
     | end |
     | turn it off |
     | turn off radio |
     | turn off music |
     | shut it off |
     | shut up |
     | be quiet |
     | end playback |
     | silence |

  Scenario Outline: pause radio playback
    When the user says "<pause the radio>"
    Then "mycroft-radio" should pause playing

   Examples: pause radio playback
     | pause the radio |
     | pause |

  Scenario Outline: play a specific radio channel
    Given nothing is playing
    When the user says "<play a specific radio channel>"
    Then "mycroft-playback-control" should reply with dialog from "just.one.moment.dialog"
    Then mycroft reply should contain "<specified channel>"
    Then "<specified channel>" should play

   Examples: play specific radio channel
     | play a specific radio channel | specified channel |
     | play the BBC radio | BBC radio |
     | Play the NPR radio | NPR radio Now |
     | Play AP hourly radio | AP Hourly Radio radio |
     | Play the radio from Associated Press | AP Hourly Radio radio |
     | Play CBC radio | CBC radio |
     | Play Fox radio | Fox radio |
     | Play PBS radio | PBS RadioHour |
     | Play YLE radio | YLE |
     | Play  DLF radio | DLF |
     | Play WDR radio | WDR |
     | play radio from bbc | BBC radio |
     | Play radio from ekot | Ekot |
     | Play financial radio | Financial Times |
     | Play radio from the Financial Times | Financial Times |

  @xfail
  Scenario Outline: give me the radio from channel
    When the user says "<give me radio from a specific channel>"
    Then mycroft reply should contain "<specified channel>"

   Examples:
     | give me radio from a specific channel | specified channel |
     | give me the radio from bbc | BBC radio |
     | give me the radio from ekot | Ekot |
     | tell me the latest NPR radio | NPR |
     | what are the latest headlines from Fox | Fox |
     | what are the headlines from WDR | WDR |

  Scenario Outline: play music with names similar to radio channels
    When the user says "<play some music>"
    Then "RadioSkill" should not reply

    Examples:
      | play some music |
      | play metallica |
      | play 1live on tunein |
      | play sunshine on tunein |
      | play bigfm on tunein |
      | Play klassik lounge easy radio |
      | play the song monkey brains |
      | play the song skinamarinky dinky dink |
      | play the song python programming |
      | play the song covid-19 |

  Scenario Outline: play radio from stations not defined in Radio Skill
    When the user says "<play some radio station>"
    Then "RadioSkill" should not reply

    Examples:
      | play some radio station |
      | play kuow |
      | play kuow radio |

  Scenario Outline: Utterances unrelated to the Radio Skill
    When the user says "<something unrelated to this skill>"
    Then "RadioSkill" should not reply

    Examples:
      | something unrelated to this skill |
      | what time is it |
      | what's the weather |
      | cancel timer |