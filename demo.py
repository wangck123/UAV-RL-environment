import imageio
import cv2
import datetime
import matplotlib.pyplot as plt

from uav_enviroment.UAV_Environment import UAVEnv
from utils.logs_callback import *

from stable_baselines import A2C
from stable_baselines import ACKTR
from stable_baselines.common.policies import MlpPolicy

NUM_CPU = 2
EXPERIMENT_NATURE = 'UAVenv_discrete_cartesian'
seed = 16


def setup_env_cart_discrete(seed):
    """
    Sets up the environment with cartesian observations and discrete action space.
    :param seed: random seed
    :return: the environment
    """
    env = UAVEnv(continuous=False, angular_movement=False, observation_with_image=False, reset_always=True,
                 controlled_speed=False)
    env.setup(n_obstacles=6, reset_always=True, threshold_dist=20, reward_sparsity=True)
    env.seed(seed)
    env = Monitor(env, log_dir, allow_early_resets=True)
    env = DummyVecEnv([lambda: env])
    return env


set_up_env = setup_env_cart_discrete

algo = 'ACKTR'
# num_timesteps = 128
num_timesteps = 18000000

if __name__ == '__main__':
    env = set_up_env(seed)

    global best_mean_reward, n_steps
    best_mean_reward, n_steps = -np.inf, 0

    """
    ACKTR(policy, env, gamma=0.99, nprocs=1, n_steps=20, ent_coef=0.01, vf_coef=0.25,
     vf_fisher_coef=1.0, learning_rate=0.25, max_grad_norm=0.5, kfac_clip=0.001,
      lr_schedule='linear', verbose=0, tensorboard_log=None, _init_setup_model=True,
       async_eigen_decomp=False, policy_kwargs=None, full_tensorboard_log=False)
    """

    model = ACKTR(policy=MlpPolicy, env=env, gamma=0.99, nprocs=1, n_steps=20,
                  ent_coef=0.01, vf_coef=0.25, vf_fisher_coef=1.0, learning_rate=0.25,
                  max_grad_norm=0.5, kfac_clip=0.001, lr_schedule='linear', verbose=0,
                  tensorboard_log=None, _init_setup_model=True)

    model.learn(total_timesteps=num_timesteps, callback=callback, seed=seed,
                log_interval=500)

    # model = ACKTR.load('/tmp/gym/best_model.pkl')
    # model.set_env(env)

    images = []
    obs = model.env.reset()
    # img = model.env.render(mode='rgb_array')
    model.env.render(mode='human')

    # for i in range(30000):
    #     # images.append(img)
    #     action, _ = model.predict(obs)
    #     obs, r, done, _ = model.env.step(action)
    #     # print(type(done[0]))
    #     # model.env.render(mode='human')
    #     if done[0]:
    #         print(done[0])
    #         model.env.render(mode='human')
    #     img = model.env.render(mode='rgb_array')
    #     cv2.imshow('image', img)
    #     cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # if i % 20 == 0 :
    #     model.env.render(mode='human')

    # imageio.mimsave('uav_learning.gif', [img for i, img in enumerate(images) if i % 5 == 0], fps=60)
    time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    trajectory_dir = './logs/Experiment_ACKTR_{}/trajectories/'.format(time)
    os.makedirs(trajectory_dir, exist_ok=True)

    print('evaluating runs')
    for i in range(100):
        episode_done = [False]
        while not episode_done[0]:
            action, _ = model.predict(obs)
            obs, r, episode_done, _ = model.env.step(action)
            fig = model.env.render(mode='human')
            if episode_done[0]:
                print(episode_done[0])
                plt.savefig('{}run_{}_r{}.png'.format(trajectory_dir, i, r))
