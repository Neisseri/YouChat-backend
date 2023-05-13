from django.test import TestCase
import random
from User.models import User, UserGroup, Contacts, FriendRequests, TokenPair
from Session.models import Session, UserAndSession, Message, UserandMessage

# Create your tests here.
class SessionTests(TestCase):
    
    # Initializer
    def setUp(self):
        # alice
        User.objects.create(name = 'swim17', password = 'abc1234567', 
                                    nickname = 'Alice', email = '17@swim.com')
        
        # bob
        User.objects.create(name = 'swim11', password = 'abc12345678', 
                                    nickname = 'Bob', email = '11@swim.com')
        
        carol = User.objects.create(name = "swim14", password = "abc1234567", 
                                    nickname = "carol", email = "14@swim.com")
        carol.save()
        
        dave = User.objects.create(name = "swim15", password = "abc12345678", 
                                    nickname = "dave", email = "15@swim.com")
        dave.save()
        
        userGroup1 = UserGroup.objects.create(user=carol)
        userGroup1.save()

        userGroup2 = UserGroup.objects.create(user=dave)
        userGroup2.save()

        contact1 = Contacts.objects.create(user=carol, friend=dave, group=userGroup1)
        contact1.save()

        contact2 = Contacts.objects.create(user=dave, friend=carol, group=userGroup2)
        contact2.save()

        session = Session.objects.create(name='friend', type=1, friend_contacts=contact1, host=carol)
        session.save()

        userAndSession1 = UserAndSession.objects.create(user=carol, session=session, permission=0)
        userAndSession1.save()

        userAndSession2 = UserAndSession.objects.create(user=dave, session=session, permission=1)
        userAndSession2.save()

        img_msg = Message.objects.create(text="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAWYAAAFeCAYAAAC2D7XWAAAMQWlDQ1BJQ0MgUHJvZmlsZQAASImVVwdYU8kWnluSkEBoAQSkhN4EkRpASggt9I4gKiEJEEqIgaBiRxcVXLtYwIauiihYAbGgiJ1FsWFfLKgo62LBrrxJAV33le/N982d//5z5j9nzp259w4Aaic4IlEuqg5AnrBQHBvsTx+XnEInPQU40AaawAo4c7gFImZ0dDiAZaj9e3l3AyDS9qq9VOuf/f+1aPD4BVwAkGiI03kF3DyIDwKAV3FF4kIAiFLebEqhSIphBVpiGCDEC6U4U46rp\
                                         DhdjvfKbOJjWRC3AaCkwuGIMwFQvQx5ehE3E2qo9kPsKOQJhACo0SH2ycvL50GcBrE1tBFBLNVnpP+gk/k3zfRhTQ4ncxjL5yIrSgGCAlEuZ9r/mY7/XfJyJUM+LGFVyRKHxErnDPN2Myc/TIpVIO4TpkdGQawJ8QcBT2YPMUrJkoQkyO1RA24BC+YM6EDsyOMEhEFsAHGQMDcyXMGnZwiC2BDDFYJOFRSy4yHWhXghvyAwTmGzWZwfq/CFNmSIWUwFf44jlvmV+rovyUlgKvRfZ/HZCn1MtTgrPgliCsTmRYLESIhVIXYoyIkLU9iMLc5iRQ7ZiCWx0vjNIY7lC4P95fpYUYY4KFZhX5Z\
                                         XMDRfbHOWgB2pwPsLs+JD5PnB2rgcWfxwLthlvpCZMKTDLxgXPjQXHj8gUD537BlfmBCn0PkgKvSPlY/FKaLcaIU9bsrPDZbyphC7FBTFKcbiiYVwQcr18QxRYXS8PE68OJsTGi2PB18GwgELBAA6kMCaDvJBNhB09DX2wTt5TxDgADHIBHxgr2CGRiTJeoTwGgeKwZ8Q8UHB8Dh/WS8fFEH+6zArv9qDDFlvkWxEDngCcR4IA7nwXiIbJRz2lggeQ0bwD+8cWLkw3lxYpf3/nh9ivzNMyIQrGMmQR7rakCUxkBhADCEGEW1wfdwH98LD4dUPViecgXsMzeO7PeEJoZPwkHCd0E24NUlQI\
                                         v4pygjQDfWDFLlI/zEXuCXUdMX9cW+oDpVxHVwf2OMu0A8T94WeXSHLUsQtzQr9J+2/zeCHp6GwIzuSUfIIsh/Z+ueRqraqrsMq0lz/mB95rOnD+WYN9/zsn/VD9nmwDfvZEluIHcDOYiex89hRrBHQsRasCWvHjknx8Op6LFtdQ95iZfHkQB3BP/wNPVlpJgscax17Hb/I+wr5U6XvaMDKF00TCzKzCulM+EXg09lCrsMoupOjkzMA0u+L/PX1Jkb23UB02r9z8/4AwLtlcHDwyHcutAWAfe5w+x/+zlkz4KdDGYBzh7kScZGcw6UXAnxLqMGdpgeMgBmwhvNxAm7AC/iBQBAKokA8SAY\
                                         TYfRZcJ2LwRQwA8wFpaAcLAOrwXqwCWwFO8EesB80gqPgJDgDLoLL4Dq4A1dPD3gB+sE78BlBEBJCRWiIHmKMWCB2iBPCQHyQQCQciUWSkTQkExEiEmQGMg8pR1Yg65EtSA2yDzmMnETOI53ILeQB0ou8Rj6hGKqCaqGGqCU6GmWgTDQMjUcnoJnoZLQYnY8uQdei1ehutAE9iV5Er6Pd6At0AAOYMqaDmWD2GANjYVFYCpaBibFZWBlWgVVjdVgzfM5XsW6sD/uIE3EaTsft4QoOwRNwLj4Zn4UvxtfjO/EGvA2/ij/A+/FvBCrBgGBH8CSwCeMImYQphFJCBWE74RDhNNxLPYR3RCJRh\
                                         2hFdId7MZmYTZxOXEzcQKwnniB2Eh8RB0gkkh7JjuRNiiJxSIWkUtI60m5SC+kKqYf0QUlZyVjJSSlIKUVJqFSiVKG0S+m40hWlp0qfyepkC7InOYrMI08jLyVvIzeTL5F7yJ8pGhQrijclnpJNmUtZS6mjnKbcpbxRVlY2VfZQjlEWKM9RXqu8V/mc8gPljyqaKrYqLJVUFYnKEpUdKidUbqm8oVKpllQ/agq1kLqEWkM9Rb1P/aBKU3VQZavyVGerVqo2qF5RfalGVrNQY6pNVCtWq1A7oHZJrU+drG6pzlLnqM9Sr1Q/rN6lPqBB0xijEaWRp7FYY5fGeY1nmiRNS81ATZ7mfM2tmqc\
                                         0H9EwmhmNRePS5tG20U7TerSIWlZabK1srXKtPVodWv3amtou2onaU7UrtY9pd+tgOpY6bJ1cnaU6+3Vu6HwaYTiCOYI/YtGIuhFXRrzXHanrp8vXLdOt172u+0mPrheol6O3XK9R754+rm+rH6M/RX+j/mn9vpFaI71GckeWjdw/8rYBamBrEGsw3WCrQbvBgKGRYbChyHCd4SnDPiMdIz+jbKNVRseNeo1pxj7GAuNVxi3Gz+nadCY9l76W3kbvNzEwCTGRmGwx6TD5bGplmmBaYlpves+MYsYwyzBbZdZq1m9ubB5hPsO81vy2BdmCYZFlscbirMV7SyvLJMsFlo2Wz6x0rdhWxVa1V\
                                         netqda+1pOtq62v2RBtGDY5NhtsLtuitq62WbaVtpfsUDs3O4HdBrvOUYRRHqOEo6pHddmr2DPti+xr7R846DiEO5Q4NDq8HG0+OmX08tFnR39zdHXMddzmeGeM5pjQMSVjmse8drJ14jpVOl1zpjoHOc92bnJ+5WLnwnfZ6HLTleYa4brAtdX1q5u7m9itzq3X3dw9zb3KvYuhxYhmLGac8yB4+HvM9jjq8dHTzbPQc7/nX172Xjleu7yejbUayx+7bewjb1NvjvcW724fuk+az2afbl8TX45vte9DPzM/nt92v6dMG2Y2czfzpb+jv9j/kP97lidrJutEABYQHFAW0BGoGZgQuD7wfpBp\
                                         UGZQbVB/sGvw9OATIYSQsJDlIV1sQzaXXcPuD3UPnRnaFqYSFhe2PuxhuG24OLw5Ao0IjVgZcTfSIlIY2RgFothRK6PuRVtFT44+EkOMiY6pjHkSOyZ2RuzZOFrcpLhdce/i/eOXxt9JsE6QJLQmqiWmJtYkvk8KSFqR1D1u9LiZ4y4m6ycLkptSSCmJKdtTBsYHjl89vifVNbU09cYEqwlTJ5yfqD8xd+KxSWqTOJMOpBHSktJ2pX3hRHGqOQPp7PSq9H4ui7uG+4Lnx1vF6+V781fwn2Z4Z6zIeJbpnbkyszfLN6siq0/AEqwXvMoOyd6U/T4nKmdHzmBuUm59nlJeWt5hoaYwR9iWb\
                                         5Q/Nb9TZCcqFXVP9py8enK/OEy8vQApmFDQVKgFf+TbJdaSXyQPinyKKos+TEmccmCqxlTh1PZpttMWTXtaHFT823R8Ond66wyTGXNnPJjJnLllFjIrfVbrbLPZ82f3zAmes3MuZW7O3N9LHEtWlLydlzSveb7h/DnzH/0S/EttqWqpuLRrgdeCTQvxhYKFHYucF61b9K2MV3ah3LG8ovzLYu7iC7+O+XXtr4NLMpZ0LHVbunEZcZlw2Y3lvst3rtBYUbzi0cqIlQ2r6KvKVr1dPWn1+QqXik1rKGska7rXhq9tWme+btm6L+uz1l+v9K+srzKoWlT1fgNvw5WNfhvrNhluKt/0abNg880\
                                         twVsaqi2rK7YStxZtfbItcdvZ3xi/1WzX316+/esO4Y7unbE722rca2p2GexaWovWSmp7d6fuvrwnYE9TnX3dlnqd+vK9YK9k7/N9aftu7A/b33qAcaDuoMXBqkO0Q2UNSMO0hv7GrMbupuSmzsOhh1ubvZoPHXE4suOoydHKY9rHlh6nHJ9/fLCluGXghOhE38nMk49aJ7XeOTXu1LW2mLaO02Gnz50JOnPqLPNsyznvc0fPe54/fIFxofGi28WGdtf2Q7+7/n6ow62j4ZL7pabLHpebO8d2Hr/ie+Xk1YCrZ66xr128Hnm980bCjZtdqV3dN3k3n93KvfXqdtHtz3fm3CXcLbunfq/i\
                                         vsH96j9s/qjvdus+9iDgQfvDuId3HnEfvXhc8PhLz/wn1CcVT42f1jxzena0N6j38vPxz3teiF587iv9U+PPqpfWLw/+5fdXe/+4/p5X4leDrxe/0Xuz463L29aB6IH77/LefX5f9kHvw86PjI9nPyV9evp5yhfSl7Vfbb42fwv7dncwb3BQxBFzZL8CGKxoRgYAr3cAQE0GgAbPZ5Tx8vOfrCDyM6sMgf+E5WdEWXEDoA7+v8f0wb+bLgD2boPHL6ivlgpANBWAeA+AOjsP16GzmuxcKS1EeA7YHPk1PS8d/JsiP3P+EPfPLZCquoCf238BkUl8jbdFinoAAACKZVhJZk1NACoAAAAIA\
                                         AQBGgAFAAAAAQAAAD4BGwAFAAAAAQAAAEYBKAADAAAAAQACAACHaQAEAAAAAQAAAE4AAAAAAAAAkAAAAAEAAACQAAAAAQADkoYABwAAABIAAAB4oAIABAAAAAEAAAFmoAMABAAAAAEAAAFeAAAAAEFTQ0lJAAAAU2NyZWVuc2hvdJdLIqgAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAHWaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA2LjAuMCI+CiAgIDxyZGY6UkRGIHhtbG5zOnJkZ\
                                         j0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgICAgIHhtbG5zOmV4aWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vZXhpZi8xLjAvIj4KICAgICAgICAgPGV4aWY6UGl4ZWxZRGltZW5zaW9uPjM1MDwvZXhpZjpQaXhlbFlEaW1lbnNpb24+CiAgICAgICAgIDxleGlmOlBpeGVsWERpbWVuc2lvbj4zNTg8L2V4aWY6UGl4ZWxYRGltZW5zaW9uPgogICAgICAgICA8ZXh\
                                         pZjpVc2VyQ29tbWVudD5TY3JlZW5zaG90PC9leGlmOlVzZXJDb21tZW50PgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KRX3AagAAABxpRE9UAAAAAgAAAAAAAACvAAAAKAAAAK8AAACvAAAGGOX8B3gAAAXkSURBVHgB7NRBDQAwDAOxlT/odRqKe7gIKifK3HfHESBAgEBGYAxzJguPECBA4AsYZkUgQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQE\
                                         DHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIEC\
                                         MQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQ\
                                         IECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHW\
                                         AQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgG\
                                         HWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUC\
                                         AgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxgQUAAP//DYos0QAABeJJREFU7dRBDQAwDAOxlT/odRqKe7gIKifK3HfHESBAgEBGYAxzJguPECBA4AsYZkUgQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHA\
                                         AEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiH\
                                         AAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXi\
                                         HAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjg\
                                         XiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJh\
                                         jgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxgQXJOXQykDmSewAAAABJRU5ErkJggg==", session=session, sender=carol, message_type="photo")
        img_msg.save()
        
        userAndMessage1 = UserandMessage.objects.create(user=carol, message=img_msg)
        userAndMessage2 = UserandMessage.objects.create(user=dave, message=img_msg)
        
    # Utility Functions
    def get_image(self, message_id):
        return self.client.get(f'/session/image?id={message_id}', content_type='application/json')
    
    def put_image(self, user_id):
        return self.client.put(f'/session/image/{user_id}')
    
    def get_message(self, user_id):
        return self.client.get(f'/session/message/{user_id}', content_type='application/json')
    
    def post_message(self, user_id, session_id, read_time):
        payload = {
            "sessionId": session_id,
            "readTime": read_time
        }
        return self.client.post(f'/session/message/{user_id}', data=payload, content_type='application/json')
    
    def get_chatroom(self, session_id):
        return self.client.get(f'/session/chatroom?id={session_id}', content_type='application/json')
    
    def put_chatroom(self, user_id, session_name, initial):
        payload = {
            'userId': user_id,
            'sessionName': session_name,
            'initial': initial
        }
        return self.client.put('/session/chatroom', data=payload, content_type='application/json')

    def post_chatroom(self, user_id, session_name, session_id):
        payload = {
            'userId': user_id,
            'sessionName': session_name,
            'sessionId': session_id
        }
        return self.client.post('/session/chatroom', data=payload, content_type='application/json')
    
    def delete_chatroom(self, user_id, session_id):
        payload = {
            'userId': user_id,
            'sessionId': session_id
        }
        return self.client.delete('/session/chatroom', data=payload, content_type='application/json')

    def put_chatroom_admin(self, user_id, session_id, applicant_id, role):
        payload = {
            'userId': user_id,
            'sessionId': session_id,
            'applicantId': applicant_id,
            'role': role
        }
        return self.client.put('/session/chatroom/Admin', data=payload, content_type='application/json')
    
    def put_translate(self, language, text):
        payload = {
            "language": language,
            "text": text
        }
        return self.client.put('/session/message/translate', data=payload, content_type='application/json')
    
    # Now start testcases

    # get image message
    def test_get_image(self):

        random.seed(1)
        res = self.get_image(1)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['image'], "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAWYAAAFeCAYAAAC2D7XWAAAMQWlDQ1BJQ0MgUHJvZmlsZQAASImVVwdYU8kWnluSkEBoAQSkhN4EkRpASggt9I4gKiEJEEqIgaBiRxcVXLtYwIauiihYAbGgiJ1FsWFfLKgo62LBrrxJAV33le/N982d//5z5j9nzp259w4Aaic4IlEuqg5AnrBQHBvsTx+XnEInPQU40AaawAo4c7gFImZ0dDiAZaj9e3l3AyDS9qq9VOuf/f+1aPD4BVwAkGiI03kF3DyIDwKAV3FF4kIAiFLebEqhSIphBVpiGCDEC6U4U46rp\
                                         DhdjvfKbOJjWRC3AaCkwuGIMwFQvQx5ehE3E2qo9kPsKOQJhACo0SH2ycvL50GcBrE1tBFBLNVnpP+gk/k3zfRhTQ4ncxjL5yIrSgGCAlEuZ9r/mY7/XfJyJUM+LGFVyRKHxErnDPN2Myc/TIpVIO4TpkdGQawJ8QcBT2YPMUrJkoQkyO1RA24BC+YM6EDsyOMEhEFsAHGQMDcyXMGnZwiC2BDDFYJOFRSy4yHWhXghvyAwTmGzWZwfq/CFNmSIWUwFf44jlvmV+rovyUlgKvRfZ/HZCn1MtTgrPgliCsTmRYLESIhVIXYoyIkLU9iMLc5iRQ7ZiCWx0vjNIY7lC4P95fpYUYY4KFZhX5Z\
                                         XMDRfbHOWgB2pwPsLs+JD5PnB2rgcWfxwLthlvpCZMKTDLxgXPjQXHj8gUD537BlfmBCn0PkgKvSPlY/FKaLcaIU9bsrPDZbyphC7FBTFKcbiiYVwQcr18QxRYXS8PE68OJsTGi2PB18GwgELBAA6kMCaDvJBNhB09DX2wTt5TxDgADHIBHxgr2CGRiTJeoTwGgeKwZ8Q8UHB8Dh/WS8fFEH+6zArv9qDDFlvkWxEDngCcR4IA7nwXiIbJRz2lggeQ0bwD+8cWLkw3lxYpf3/nh9ivzNMyIQrGMmQR7rakCUxkBhADCEGEW1wfdwH98LD4dUPViecgXsMzeO7PeEJoZPwkHCd0E24NUlQI\
                                         v4pygjQDfWDFLlI/zEXuCXUdMX9cW+oDpVxHVwf2OMu0A8T94WeXSHLUsQtzQr9J+2/zeCHp6GwIzuSUfIIsh/Z+ueRqraqrsMq0lz/mB95rOnD+WYN9/zsn/VD9nmwDfvZEluIHcDOYiex89hRrBHQsRasCWvHjknx8Op6LFtdQ95iZfHkQB3BP/wNPVlpJgscax17Hb/I+wr5U6XvaMDKF00TCzKzCulM+EXg09lCrsMoupOjkzMA0u+L/PX1Jkb23UB02r9z8/4AwLtlcHDwyHcutAWAfe5w+x/+zlkz4KdDGYBzh7kScZGcw6UXAnxLqMGdpgeMgBmwhvNxAm7AC/iBQBAKokA8SAY\
                                         TYfRZcJ2LwRQwA8wFpaAcLAOrwXqwCWwFO8EesB80gqPgJDgDLoLL4Dq4A1dPD3gB+sE78BlBEBJCRWiIHmKMWCB2iBPCQHyQQCQciUWSkTQkExEiEmQGMg8pR1Yg65EtSA2yDzmMnETOI53ILeQB0ou8Rj6hGKqCaqGGqCU6GmWgTDQMjUcnoJnoZLQYnY8uQdei1ehutAE9iV5Er6Pd6At0AAOYMqaDmWD2GANjYVFYCpaBibFZWBlWgVVjdVgzfM5XsW6sD/uIE3EaTsft4QoOwRNwLj4Zn4UvxtfjO/EGvA2/ij/A+/FvBCrBgGBH8CSwCeMImYQphFJCBWE74RDhNNxLPYR3RCJRh\
                                         2hFdId7MZmYTZxOXEzcQKwnniB2Eh8RB0gkkh7JjuRNiiJxSIWkUtI60m5SC+kKqYf0QUlZyVjJSSlIKUVJqFSiVKG0S+m40hWlp0qfyepkC7InOYrMI08jLyVvIzeTL5F7yJ8pGhQrijclnpJNmUtZS6mjnKbcpbxRVlY2VfZQjlEWKM9RXqu8V/mc8gPljyqaKrYqLJVUFYnKEpUdKidUbqm8oVKpllQ/agq1kLqEWkM9Rb1P/aBKU3VQZavyVGerVqo2qF5RfalGVrNQY6pNVCtWq1A7oHZJrU+drG6pzlLnqM9Sr1Q/rN6lPqBB0xijEaWRp7FYY5fGeY1nmiRNS81ATZ7mfM2tmqc\
                                         0H9EwmhmNRePS5tG20U7TerSIWlZabK1srXKtPVodWv3amtou2onaU7UrtY9pd+tgOpY6bJ1cnaU6+3Vu6HwaYTiCOYI/YtGIuhFXRrzXHanrp8vXLdOt172u+0mPrheol6O3XK9R754+rm+rH6M/RX+j/mn9vpFaI71GckeWjdw/8rYBamBrEGsw3WCrQbvBgKGRYbChyHCd4SnDPiMdIz+jbKNVRseNeo1pxj7GAuNVxi3Gz+nadCY9l76W3kbvNzEwCTGRmGwx6TD5bGplmmBaYlpves+MYsYwyzBbZdZq1m9ubB5hPsO81vy2BdmCYZFlscbirMV7SyvLJMsFlo2Wz6x0rdhWxVa1V\
                                         netqda+1pOtq62v2RBtGDY5NhtsLtuitq62WbaVtpfsUDs3O4HdBrvOUYRRHqOEo6pHddmr2DPti+xr7R846DiEO5Q4NDq8HG0+OmX08tFnR39zdHXMddzmeGeM5pjQMSVjmse8drJ14jpVOl1zpjoHOc92bnJ+5WLnwnfZ6HLTleYa4brAtdX1q5u7m9itzq3X3dw9zb3KvYuhxYhmLGac8yB4+HvM9jjq8dHTzbPQc7/nX172Xjleu7yejbUayx+7bewjb1NvjvcW724fuk+az2afbl8TX45vte9DPzM/nt92v6dMG2Y2czfzpb+jv9j/kP97lidrJutEABYQHFAW0BGoGZgQuD7wfpBp\
                                         UGZQbVB/sGvw9OATIYSQsJDlIV1sQzaXXcPuD3UPnRnaFqYSFhe2PuxhuG24OLw5Ao0IjVgZcTfSIlIY2RgFothRK6PuRVtFT44+EkOMiY6pjHkSOyZ2RuzZOFrcpLhdce/i/eOXxt9JsE6QJLQmqiWmJtYkvk8KSFqR1D1u9LiZ4y4m6ycLkptSSCmJKdtTBsYHjl89vifVNbU09cYEqwlTJ5yfqD8xd+KxSWqTOJMOpBHSktJ2pX3hRHGqOQPp7PSq9H4ui7uG+4Lnx1vF6+V781fwn2Z4Z6zIeJbpnbkyszfLN6siq0/AEqwXvMoOyd6U/T4nKmdHzmBuUm59nlJeWt5hoaYwR9iWb\
                                         5Q/Nb9TZCcqFXVP9py8enK/OEy8vQApmFDQVKgFf+TbJdaSXyQPinyKKos+TEmccmCqxlTh1PZpttMWTXtaHFT823R8Ond66wyTGXNnPJjJnLllFjIrfVbrbLPZ82f3zAmes3MuZW7O3N9LHEtWlLydlzSveb7h/DnzH/0S/EttqWqpuLRrgdeCTQvxhYKFHYucF61b9K2MV3ah3LG8ovzLYu7iC7+O+XXtr4NLMpZ0LHVbunEZcZlw2Y3lvst3rtBYUbzi0cqIlQ2r6KvKVr1dPWn1+QqXik1rKGska7rXhq9tWme+btm6L+uz1l+v9K+srzKoWlT1fgNvw5WNfhvrNhluKt/0abNg880\
                                         twVsaqi2rK7YStxZtfbItcdvZ3xi/1WzX316+/esO4Y7unbE722rca2p2GexaWovWSmp7d6fuvrwnYE9TnX3dlnqd+vK9YK9k7/N9aftu7A/b33qAcaDuoMXBqkO0Q2UNSMO0hv7GrMbupuSmzsOhh1ubvZoPHXE4suOoydHKY9rHlh6nHJ9/fLCluGXghOhE38nMk49aJ7XeOTXu1LW2mLaO02Gnz50JOnPqLPNsyznvc0fPe54/fIFxofGi28WGdtf2Q7+7/n6ow62j4ZL7pabLHpebO8d2Hr/ie+Xk1YCrZ66xr128Hnm980bCjZtdqV3dN3k3n93KvfXqdtHtz3fm3CXcLbunfq/i\
                                         vsH96j9s/qjvdus+9iDgQfvDuId3HnEfvXhc8PhLz/wn1CcVT42f1jxzena0N6j38vPxz3teiF587iv9U+PPqpfWLw/+5fdXe/+4/p5X4leDrxe/0Xuz463L29aB6IH77/LefX5f9kHvw86PjI9nPyV9evp5yhfSl7Vfbb42fwv7dncwb3BQxBFzZL8CGKxoRgYAr3cAQE0GgAbPZ5Tx8vOfrCDyM6sMgf+E5WdEWXEDoA7+v8f0wb+bLgD2boPHL6ivlgpANBWAeA+AOjsP16GzmuxcKS1EeA7YHPk1PS8d/JsiP3P+EPfPLZCquoCf238BkUl8jbdFinoAAACKZVhJZk1NACoAAAAIA\
                                         AQBGgAFAAAAAQAAAD4BGwAFAAAAAQAAAEYBKAADAAAAAQACAACHaQAEAAAAAQAAAE4AAAAAAAAAkAAAAAEAAACQAAAAAQADkoYABwAAABIAAAB4oAIABAAAAAEAAAFmoAMABAAAAAEAAAFeAAAAAEFTQ0lJAAAAU2NyZWVuc2hvdJdLIqgAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAHWaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA2LjAuMCI+CiAgIDxyZGY6UkRGIHhtbG5zOnJkZ\
                                         j0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgICAgIHhtbG5zOmV4aWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vZXhpZi8xLjAvIj4KICAgICAgICAgPGV4aWY6UGl4ZWxZRGltZW5zaW9uPjM1MDwvZXhpZjpQaXhlbFlEaW1lbnNpb24+CiAgICAgICAgIDxleGlmOlBpeGVsWERpbWVuc2lvbj4zNTg8L2V4aWY6UGl4ZWxYRGltZW5zaW9uPgogICAgICAgICA8ZXh\
                                         pZjpVc2VyQ29tbWVudD5TY3JlZW5zaG90PC9leGlmOlVzZXJDb21tZW50PgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KRX3AagAAABxpRE9UAAAAAgAAAAAAAACvAAAAKAAAAK8AAACvAAAGGOX8B3gAAAXkSURBVHgB7NRBDQAwDAOxlT/odRqKe7gIKifK3HfHESBAgEBGYAxzJguPECBA4AsYZkUgQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQE\
                                         DHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIEC\
                                         MQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQ\
                                         IECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHW\
                                         AQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgG\
                                         HWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUC\
                                         AgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxgQUAAP//DYos0QAABeJJREFU7dRBDQAwDAOxlT/odRqKe7gIKifK3HfHESBAgEBGYAxzJguPECBA4AsYZkUgQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHA\
                                         AEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiH\
                                         AAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXi\
                                         HAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjg\
                                         XiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJh\
                                         jgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxAcMcC8Q7BAgQMMw6QIAAgZiAYY4F4h0CBAgYZh0gQIBATMAwxwLxDgECBAyzDhAgQCAmYJhjgXiHAAEChlkHCBAgEBMwzLFAvEOAAAHDrAMECBCICRjmWCDeIUCAgGHWAQIECMQEDHMsEO8QIEDAMOsAAQIEYgKGORaIdwgQIGCYdYAAAQIxgQXJOXQykDmSewAAAABJRU5ErkJggg==")


    # upload head portrait
    def test_upload_portrait(seld):

        random.seed(2)

    def test_get_chatroom(self):

        random.seed(123)
        res = self.get_chatroom(1)

        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['sessionName'], 'friend')
        self.assertEqual(res.json()['members'][0]['id'], 3)
        self.assertEqual(res.json()['members'][0]['nickname'], 'carol')
        self.assertEqual(res.json()['members'][0]['role'], 0)
        self.assertEqual(res.json()['members'][1]['id'], 4)
        self.assertEqual(res.json()['members'][1]['nickname'], 'dave')
        self.assertEqual(res.json()['members'][1]['role'], 1)

    # create chatroom
    def test_put_chatroom(self):

        random.seed(5)
        alice = User.objects.filter(name='swim17').first()
        res = self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])

        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

    # create chatroom for unexisted user
    def test_put_chatroom_user_unexisted(self):

        random.seed(6)
        res = self.put_chatroom(10086, 'chatroom', [10086])

        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'User Not Existed')

    # add user to a specific chatroom
    def test_post_chatroom(self):

        random.seed(7)
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        bob = User.objects.filter(name='swim11').first()
        res = self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    # add user to a specific chatroom with unexisted user
    def test_post_chatroom_user_unexisted(self):

        random.seed(8)
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        res = self.post_chatroom(10086, chatroom.name, chatroom.session_id)

        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User Not Existed')

    # add user to a specific chatroom with unexisted session
    def test_post_chatroom_session_unexisted(self):

        random.seed(9)
        alice = User.objects.filter(name='swim17').first()
        res = self.post_chatroom(alice.user_id, 'abaababa', '100000')

        self.assertEqual(res.json()['info'], 'Session Not Existed')
        self.assertEqual(res.json()['code'], 2)

    # quit from a chatroom
    def test_delete_chatroom(self):

        random.seed(10)
        # Alice create chatroom
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        # Bob join chatroom
        bob = User.objects.filter(name='swim11').first()
        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        # Bob quit from the chatroom
        res = self.delete_chatroom(bob.user_id, chatroom.session_id)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    # quit from a chatroom with unexisted user
    def test_delete_chatroom_user_unexisted(self):

        random.seed(11)
        # Alice create chatroom
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        res = self.delete_chatroom(10086, chatroom.session_id)

        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User Not Existed')

    # quit from a chatroom with unexisted session
    def test_delete_chatroom_session_unexisted(self):

        random.seed(12)
        bob = User.objects.filter(name='swim11').first()
        res = self.delete_chatroom(bob.user_id, 100000)

        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'Session Not Existed')

    # agree application for joining chatroom
    def test_put_chatroom_admin(self):

        random.seed(13)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(alice.user_id, chatroom.session_id, bob.user_id, 2)

        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

    # agree application for joining chatroom with Not-Admin
    def test_put_chatroom_admin_not_admin(self):

        random.seed(14)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(bob.user_id, chatroom.session_id, bob.user_id, 2)

        self.assertEqual(res.json()['info'], 'User Not Existed or Permission Denied')
        self.assertEqual(res.json()['code'], 1)

    # agree application for joining chatroom with unexisted session
    def test_put_chatroom_admin_session_unexisted(self):

        random.seed(15)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(alice.user_id, 1000000, bob.user_id, 2)

        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'Session Not Existed')

    # agree application for joining chatroom with unexisted applicant
    def test_put_chatroom_admin_applicant_unexisted(self):

        random.seed(16)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(alice.user_id, chatroom.session_id, 10086, 2)

        self.assertEqual(res.json()['code'], 3)
        self.assertEqual(res.json()['info'], 'Applicant Not Existed')

    # agree application for joining chatroom with applicant already in session
    # def test_put_chatroom_admin_applicant_in_session(self):

    #     random.seed(17)
    #     alice = User.objects.filter(name='swim17').first()
    #     bob = User.objects.filter(name='swim11').first()
    #     self.put_chatroom(alice.user_id, 'chatroom', [alice.user_id])
    #     chatroom = Session.objects.filter(name='chatroom').first()

    #     self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

    #     self.put_chatroom_admin(alice.user_id, chatroom.session_id, bob.user_id, 2)
    #     res = self.put_chatroom_admin(alice.user_id, chatroom.session_id, bob.user_id, 2)

    #     self.assertEqual(res.json()['info'], 'Already In Session')
    #     self.assertEqual(res.json()['code'], 4)

    def test_get_message(self):

        random.seed(18)
        res = self.get_message(3)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['data']), 1)
        self.assertEqual(res.json()['data'][0]['sessionId'], 1)
        self.assertEqual(res.json()['data'][0]['sessionName'], "friend")
        self.assertEqual(res.json()['data'][0]['sessionType'], 1)
        self.assertEqual(res.json()['data'][0]['type'], "photo")
        self.assertEqual(res.json()['data'][0]['lastSender'], "swim14")
        self.assertEqual(res.json()['data'][0]['isTop'], False)
        self.assertEqual(res.json()['data'][0]['isMute'], False)

    def test_post_message(self):

        random.seed(18)
        timestamp = 1682509113
        res = self.post_message(3, 1, timestamp)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()['code'], 0)

    # def test_put_translate(self):

    #     random.seed(19)
    #     res = self.put_translate("English", "software engineering")
    #     self.assertEqual(res.json()['info'], 'Succeed')
    #     self.assertEqual(res.json()['code'], 0)
    #     self.assertEqual(res.json()['text'], "软件工程")
        