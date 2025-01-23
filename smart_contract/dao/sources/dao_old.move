// /*
// /// Module: dao
// module dao::dao;
// */
//
// // For Move coding conventions, see
// // https://docs.sui.io/concepts/sui-move-concepts/conventions
//
//
// module dao::dao{
//     use std::debug;
//     use std::option::{Self,Option};
//     use std::string::String;
//     use sui::coin::{Self, Coin};
//     use sui::balance::{Self, Balance,Supply};
//     use sui::object::{Self, ID, UID};
//     use sui::transfer;
//     use sui::tx_context::{Self, TxContext};
//
//     const EInvailVotes:u64 = 4;
//     const ETaskNotPassed:u64 = 5;
//     const ETaskNotClosed:u64 = 6;
//     const ERoleCheck:u64 = 7;
//     const ETaskStatus:u64 = 8;
//     const EOrganizationStatus:u64 = 9;
//     const ETaskHandlerCheck:u64 = 10;
//     const EInsufficientTreasurySupply:u64 = 11;
//     const EAlreadyClaimed:u64 = 12;
//
//
//     const MAX_VOTES_ONE_TIME: u64 = 10;
//     const TOTAL_SUPPLY:u64 = 100_000_000_000_000_000;
//
//      struct DAO has drop{}
//      struct Dao<phantom T> has key{
//         id: UID,
//         total_members: u64, //Total Number of DAO Members
//         total_supply: Supply<T>, //Total Supply of DAO Tokens
//     }
//     //Treasury of the DAO
//      struct Treasury<phantom T> has key,store{
//         id:UID,
//         supply: Balance<T>, //Balance Stored in the Treasury
//     }
//      struct VoteCap has key{
//         id: UID,
//         voter: address,
//         votes: u64,
//         task_id: ID,
//         organization_id: ID,
//         is_support: bool,
//     }
//      struct OrganizationTask has key,store {
//         id:UID,
//         title: String, //The title of the task
//         describe: String,
//         reward_amount: u64,
//         organization_id:ID,
//         handler: Option<address>, //处理者的地址
//         support: u64, //支持者的数量
//         against: u64, //反对者的数量
//         is_closed: bool,
//         is_passed: bool,
//         is_claimed_reward: bool,
//
//     }
//      struct TaskRewardCap has key{
//         id:UID,
//         reward_amount: u64,
//         task_id: ID,
//         owner: address,
//     }
//
//      struct InitCoreCap has key{
//         id: UID,
//         role_address:address,
//     }
//
//      struct CoreCap has key{
//         id: UID,
//         role_address:address,
//     }
//
//      struct MemberCap has key{
//         id: UID,
//         role_address:address,
//     }
//     // user organization info
//      struct Organization has key,store{
//         id: UID,
//         name: String,
//         description: String,
//         total_members: u64,
//         role_address:address,
//     }
//      struct OrganizationMemberCap has key{
//         id: UID,
//         organization_id: ID,
//         role_address:address,
//     }
//
//
//     fun init(witness: DAO, ctx: &mut TxContext) {
//         //1. create dao token and mint supply
//         let (treasury_cap,metadata) = coin::create_currency<DAO>(
//             witness,
//             18,
//             b"DAO",
//             b"dao",
//             b"Dao token.",
//             option::none(),
//             ctx);
//         transfer::public_freeze_object(metadata);
//         let total_balance = coin::mint_balance<DAO>(&mut treasury_cap, TOTAL_SUPPLY);
//
//         //2. move supply to treasury and share treasury
//         let treasury = Treasury<DAO> {
//             id: object::new(ctx),
//             supply: total_balance,
//         };
//         transfer::share_object(treasury);
//
//         //3.create dao metadata and share metadata
//         let total_supply = coin::treasury_into_supply<DAO>(treasury_cap);
//
//         let dao = Dao{
//             id: object::new(ctx),
//             total_members: 1,
//             total_supply: total_supply,
//         };
//         transfer::share_object(dao);
//
//         //4. mint Cap to msg.sender
//         let msg_sender = tx_context::sender(ctx);
//
//         let init_core_cap = InitCoreCap{
//             id: object::new(ctx),
//             role_address: msg_sender,
//         };
//         let core_cap = CoreCap{
//             id: object::new(ctx),
//             role_address: msg_sender,
//         };
//         let member_cap = MemberCap{
//             id: object::new(ctx),
//             role_address: msg_sender,
//         };
//
//         transfer::transfer(member_cap,msg_sender);
//         transfer::transfer(core_cap, msg_sender);
//         transfer::transfer(init_core_cap, msg_sender);
//     }
//     public fun init_organization(
//         member_cap:& MemberCap,
//         name:String,
//         description:String,
//         user_address:address,
//         ctx: &mut TxContext
//     ) {
//         check_membercap_role(member_cap,ctx);
//         let sender = tx_context::sender(ctx);
//         debug::print(& sender);
//         let org = Organization{
//             id: object::new(ctx),
//             name: name,
//             description: description,
//             total_members: 1,
//             role_address:sender,
//         };
//         let org_member_cap = OrganizationMemberCap{
//             id: object::new(ctx),
//             organization_id: object::uid_to_inner(&org.id),
//             role_address:user_address,
//         };
//         transfer::transfer(org_member_cap, user_address);
//         transfer::transfer(org, sender);// 由agent发起组织的初始化，然后这个组织的所有权归agent所有
//     }
//     public fun add_core_member(
//         init_core_cap: & InitCoreCap,
//         user_address :address,
//         ctx: &mut TxContext
//     ){
//         check_init_corecap_role(init_core_cap,ctx);
//         let core_cap = CoreCap{
//             id: object::new(ctx),
//             role_address:user_address,
//         };
//         transfer::transfer(core_cap, user_address);
//     }
//     public fun add_member(
//         core_cap:& CoreCap,
//         user_address :address,
//         ctx: &mut TxContext
//     ){
//         check_corecap_role(core_cap,ctx);
//         let member_cap = MemberCap{
//             id: object::new(ctx),
//             role_address:user_address,
//         };
//         transfer::transfer(member_cap, user_address);
//     }
//
//     //加入组织只能由agent发起
//     public fun add_organization_member(
//         member_cap:& MemberCap,
//         org :&mut Organization,
//         user_address:address,
//         ctx: &mut TxContext
//     ){
//         check_membercap_role(member_cap,ctx);
//         let org_members = & org.total_members;
//         org.total_members = *org_members + 1;
//         let org_member_cap = OrganizationMemberCap{
//             id: object::new(ctx),
//             organization_id: object::uid_to_inner(&org.id),
//             role_address:user_address,
//         };
//         transfer::transfer(org_member_cap, user_address);
//     }
//
//
//     //==========task==========
//     //只能由agent发起任务
//     public fun set_community_task(
//         member_cap:& MemberCap,
//         org :& Organization,
//         title: String,
//         describe:String,
//         reward_amount:u64,
//         ctx:&mut TxContext
//     ){
//         check_membercap_role(member_cap,ctx);
//         let new_task = OrganizationTask{
//             id: object::new(ctx),
//             title:title,
//             describe:describe,
//             reward_amount:reward_amount,
//             organization_id:object::uid_to_inner(&org.id),
//             handler: option::none(),
//             support: 0,
//             against: 0,
//             is_closed: false,
//             is_passed: false,
//             is_claimed_reward: false,
//         };
//         transfer::share_object(new_task);
//     }
//     //成员领取任务
//     public fun get_task(
//         org_cap:& OrganizationMemberCap,
//         task:&mut OrganizationTask,
//         ctx:&mut TxContext
//     ){
//         check_organization_role(org_cap,ctx);
//         assert!(task.is_closed == true, ETaskStatus);
//         assert!(task.organization_id == org_cap.organization_id, EOrganizationStatus);
//
//         assert!(option::is_some(&task.handler), ETaskHandlerCheck);
//
//         task.handler = option::some<address>(tx_context::sender(ctx));
//     }
//
//     //组织成员投票关闭task,投票超过一半都会导致task关闭, 返回vote凭证防止反复请求，投票需要质押代币，减少重入的可能性
//     public fun vote_task(
//         org_cap:& OrganizationMemberCap,
//         task:&mut OrganizationTask,
//         org: &Organization,
//         treasury:&mut Treasury<DAO>,
//         coin:&mut Coin<DAO>,
//         votes: u64,
//         is_support:bool,
//         ctx:&mut TxContext
//     ){
//         check_organization_role(org_cap,ctx);
//         assert!(task.is_closed == true, ETaskStatus);
//         assert!(task.organization_id == org_cap.organization_id, EOrganizationStatus);
//         assert!(option::is_some<address>(&task.handler), ETaskHandlerCheck);
//         assert!(votes >= 1  && votes <= MAX_VOTES_ONE_TIME, EInvailVotes);
//
//         let task_handler = option::borrow<address>(&task.handler);
//
//         // 质押代币到treasury
//         transfer_coin_to_treasury(treasury,coin,votes);
//         if (is_support) {
//             task.support = task.support + votes;
//         }
//         else {
//             task.against = task.against + votes;
//         };
//
//         let standard_num =  org.total_members / 2 + 1;
//         if (task.support >= standard_num) {
//             task.is_closed = true;
//             task.is_passed = true;
//         };
//         if (task.against >= standard_num) {
//             task.is_closed = true;
//             task.is_passed = false;
//         };
//
//         if (task.is_passed) {
//             //如果任务被组织成员认为是通过了，就可以领取奖励，奖励以对象的方式发放，object可以明显表达task信息
//             let reward_cap = TaskRewardCap{
//                 id: object::new(ctx),
//                 reward_amount:task.reward_amount,
//                 task_id: object::uid_to_inner(&task.id),
//                 owner:*task_handler,
//             };
//             transfer::transfer(reward_cap,*task_handler);
//         };
//         let vote_cap = VoteCap {
//             id: object::new(ctx),
//             task_id: object::uid_to_inner(&task.id),
//             organization_id: object::uid_to_inner(&org.id),
//             voter: org_cap.role_address,
//             is_support: is_support,
//             votes: votes,
//         };
//         transfer::transfer(vote_cap, org_cap.role_address);
//
//     }
//     //领取任务奖励
//     public fun claim_task_reward(
//         org_cap:& OrganizationMemberCap,
//         task:&mut OrganizationTask,
//         treasury:&mut Treasury<DAO> ,
//         reward_cap:&mut TaskRewardCap,
//         ctx:&mut TxContext
//     ){
//         // 1.veriry the parameters
//         check_organization_role(org_cap,ctx);
//         assert!(task.is_passed, ETaskNotPassed);
//         assert!(!task.is_claimed_reward, EAlreadyClaimed);
//         assert!(option::is_some<address>(&task.handler), ETaskHandlerCheck);
//         let task_handler = option::borrow<address>(&task.handler);
//         assert!(*task_handler == tx_context::sender(ctx), ERoleCheck);
//
//         task.is_claimed_reward = true;
//         let reward_coin = take_coin_from_treasury(treasury,reward_cap.reward_amount,ctx);
//         transfer::public_transfer(reward_coin,*task_handler);
//     }
//     //将质押的token返回到钱包
//     public fun claim_task_vote(
//         org_cap:& OrganizationMemberCap,
//         vote_cap: VoteCap,
//         treasury:&mut Treasury<DAO>,
//         task:&mut OrganizationTask,
//         ctx:&mut TxContext
//     ){
//         // 1.veriry the parameters
//         check_organization_role(org_cap,ctx);
//         assert!(&vote_cap.task_id == object::borrow_id(task), ETaskStatus);
//         assert!(task.is_closed, ETaskNotClosed);
//         assert!(org_cap.role_address == vote_cap.voter, ERoleCheck);
//
//         // 2.delete voteCap
//         let VoteCap {id, voter, votes,task_id,organization_id,is_support} = vote_cap;
//         object::delete(id);
//
//         // 3.take coin from treasury
//         let reward_coin = take_coin_from_treasury(treasury,votes,ctx);
//
//         // 4.transfer coin to voter
//         transfer::public_transfer(reward_coin,voter);
//     }
//
//
//     //==========internal==========
//     fun transfer_coin_to_treasury(treasury:&mut Treasury<DAO>,coin:&mut Coin<DAO>,amount: u64){
//         assert!(balance::value<DAO>(&treasury.supply) >= amount, EInsufficientTreasurySupply);
//         balance::join<DAO>(
//             &mut treasury.supply,
//             balance::split<DAO>(
//                 coin::balance_mut(coin),
//                 amount
//             )
//         );
//     }
//     fun take_coin_from_treasury(treasury:&mut Treasury<DAO>,amount: u64,ctx:&mut TxContext): Coin<DAO>{
//         let supply = &mut treasury.supply;
//         let reward_coin = coin::take<DAO>(supply, amount, ctx);
//         reward_coin
//     }
//
//     fun check_init_corecap_role(init_core_cap:& InitCoreCap,ctx: & TxContext){
//         assert!(init_core_cap.role_address== tx_context::sender(ctx), ERoleCheck);
//     }
//
//     fun check_corecap_role(core_cap:& CoreCap,ctx: & TxContext){
//         assert!(core_cap.role_address== tx_context::sender(ctx), ERoleCheck);
//     }
//
//
//     fun check_membercap_role(member_cap:& MemberCap,ctx: & TxContext){
//         assert!(member_cap.role_address == tx_context::sender(ctx), ERoleCheck);
//     }
//     fun check_organization_role(org:& OrganizationMemberCap,ctx: & TxContext){
//         assert!(org.role_address == tx_context::sender(ctx), ERoleCheck);
//     }
//     #[test_only]
//     /// Wrapper of module initializer for testing
//     public fun test_init(ctx: &mut TxContext) {
//         init(DAO {}, ctx)
//     }
//     #[test]
//     public fun test(){
//         use sui::test_scenario;
//         use std::string::{Self};
//         use std::debug;
//         // Initialize a mock sender address
//         let addr1 = @0xa;
//         let addr2 = @0xb;
//         let addr3 = @0xc;
//
//         // Begins a multi-transaction scenario with addr1 as the sender
//         let scenario = test_scenario::begin(addr1);
//
//         //1. dao deploy
//         test_init(test_scenario::ctx(&mut scenario));
//         //2. set community task
//         {
//             test_scenario::next_tx(&mut scenario, addr1);
//
//             let member_cap = test_scenario::take_from_sender<MemberCap>(& scenario);
//             let ctx = test_scenario::ctx(&mut scenario);
//             init_organization(
//                 &member_cap,
//                 string::utf8(b"The first organization"),
//                 string::utf8(b"org1 desc"),
//                 addr2,
//                 ctx,
//                 );
//
//             debug::print(& member_cap);
//             test_scenario::return_to_sender(& scenario, member_cap);
//         };
//         test_scenario::end(scenario);
//     }
// }