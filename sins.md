* Pretty sure the git poller can be simplified
* Not handling repos that we can't force push to main
* slack_dao isn't 'chat_dao' - this is gross, but only supporting one type of chat for now, non prod, don't mind blowing away dbs at this stage
* only polling, no webhooks, so high latency and extra state to manage - but poll first as we'll always need to be able to recover from failures, driving down latency is purely an optimization