# Risk Log

## Key

### Frequency Ratings
| Number | Name     | Meaning                                     |
|--------|----------|---------------------------------------------|
| 0      | Never    | Can't happen                                |
| 1      | Rare     | Could go years without happening            |
| 2      | Uncommon | Could go one or two years without happening |
| 3      | Moderate | Could go months without happening           |
| 4      | Common   | Could happen once or twice a month          |
| 5      | Frequent | Could happen once or twice a week           |

### Impact Ratings
| Number | Name     | Meaning                                                                                                       |
|--------|--------------|-----------------------------------------------------------------------------------------------------------|
| 0      | No impact    | No impact whatsoever                                                                                      |
| 1      | Minimal      | Trivial to mitigate, &lt;hour                                                                             |
| 2      | Low          | Few hours, cost &lt;\$25, noticeable by a user                                                            |
| 3      | Moderate     | Day or two, cost &lt;\$100, damage to a user or noticeable by multiple users                              |
| 4      | High         | Major harm to a user, or moderate harm to a few users, service interruption                               |
| 5      | Catastrophic | Significant harm to many users or impact over 25% of users, potential for indefinite service interruption |

### Overall Risk Assessment
Product of the numerical values for frequency and impact ratings. Inherent risk is risk
before mitigation, and residual risk is after mitigation. These are labeled as
`XXR, XXI`.

## Risks
Risks are ordered from the highest risk assessment (residual) to the lowest, and
alphabetical in case of a tie.

### Cross-Site Scripting Attack - 10R, 20I
| Residual Frequency | Residual Impact  | Inherent Frequency | Inherent Impact  |
|--------------------|------------------|--------------------|------------------|
| 2 (Uncommon)       | 5 (Catastrophic) | 4 (Common)         | 5 (Catastrophic) |

Our app, in order to properly display RSS feed and item descriptions, has to parse HTML
included in an XML feed we pull from an externally-controlled server. It is not unlikely
that, if we pull hundreds of feeds a week, we will sometimes encounter a feed that
attempts an XSS attack by putting a script in the description. As such, before
mitigation, we rank the frequency as Common.

Additionally, since our app controls and authorizes payment on the frontend, a XSS
attack could potentially control connected wallets of any user accessing the infected
page. If users do not have proper budgets configured, this could lead to major financial
harm for many users. As such, we've ranked the impact as Catastrophic.

Our mitigation for this is to handle parsing of feed and item descriptions on the
backend, and convert only specific tags into elements of our choosing. For instance, 
headers could be converted to bolded text. This description can then be sent to the 
frontend as JSON, where it will be parsed and converted into a premade set of
components. This process will prevent any tags not explicitly whitelisted by us, such as
the script tag, from being rendered in the DOM. However, it is not inconceivable that, 
somewhat far in the future, a change could be made to our application that renders it
vulnerable to such an attack. As such, after mitigation, we consider the frequency to
be Uncommon.

This risk is currently our biggest concern regarding security. Perhaps mitigations such
as additional documentation, CI checks, and changes to our code review process could
further reduce this risk. It would be beneficial to lower the impact.

### SQL Injection Attack on the PodcastIndex via our Search Feature - 4R, 16I
| Residual Frequency | Residual Impact  | Inherent Frequency | Inherent Impact  |
|--------------------|------------------|--------------------|------------------|
| 1 (Rare)           | 4 (High)         | 4 (Common)         | 4 (High)         |

Our app currently passes search queries to the PodcastIndex API to power our search 
feature. However, if a malicous user were to pass an SQL injection payload through our
search feature and our app doesn't block it, it would then go to the PodcastIndex, where
it would be up to their system to identify and block it. If we were to have a few 
thousand users daily, it is not unlikely that some users would attempt this attack. As
such, the inherent frequency has been rated as Common.

If such an attack were to get through our backend undetected and be passed to the 
PodcastIndex, it could harm our relationship with them, possibly causing us to lose our
API access, or worse, resulting in a successful attack on the PodcastIndex. Both 
situations would result in significant loss of service in our app. Our app could still
function without the PodcastIndex, but there aren't really any alternatives to their
service, other than indexing feeds ourselves. If we don't have a large enough user base,
we likely won't have enough feeds indexed to appeal to users. Since no users would be
directly harmed, but our service would be significantly impacted, we've ranked the
inherent impact as High.

We currently mitigate this by using regex to check for SQL injection attacks, and have
integration tests that verify SQL injection attacks do not make it through to the 
PodcastIndex when sent to our search endpoints. Additionally, we plan to have the 
search feature instead search our database of feeds, which only occasionally polls the
PodcastIndex for new feeds. As such, even a successful SQL injection attack should never
make it to the PodcastIndex's API. Since, only by reintroducing functionality to pass
searches to the PodcastIndex, could this attack make it through after our mitigations,
we've ranked the residual frequency as Rare.

### The PodcastIndex Experiences a Service Interruption - 2R, 6I
| Residual Frequency | Residual Impact  | Inherent Frequency | Inherent Impact  |
|--------------------|------------------|--------------------|------------------|
| 2 (Uncommon)       | 1 (Minimal)      | 2 (Uncommon)       | 3 (Moderate)     |

Our app currently relies on the PodcastIndex for searching feeds. This is a feature that
a lot of users are likely to use. If the PodcastIndex were to experience a service 
interruption, it could impact our ability to offer this feature. Since the PodcastIndex
has a large community surrounding it and is well maintained, service interruptions are
not likely to occur. However, no software service is immune to cyberattacks or mistakes
in deployment, so we've ranked the frequency of this event as Uncommon.

If the PodcastIndex were to go down, we would be unable to search their database for
feeds, and, in its current state, our search feature would not be able to function.
Since this is a feature likely to be used by a lot of users, it is likely this would 
have a noticeable impact on a lot of users, so we've ranked its impact as Moderate.

One way we intend to mitigate this is to instead search our database for feeds and
tracks, which, in addition to allowing us to further refine a search, would allow us to
continue providing our search feature in the event of a PodcastIndex outage. We would be
unable to update our database with new feeds that have been added to the PodcastIndex,
but, if they're down anyway, its unlikely users would notice. As such, after mitigation
is applied, the impact will be re-evaluated to be Minimal.

