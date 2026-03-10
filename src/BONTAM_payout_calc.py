


def average_tamar(observed_TAMAR, simulated_tamar, business_days_till_expiry):
  '''this function takes business days from the most recent TAMAR publication until 10 business days before expiry, as well as the historical TAMAR (automatically started
  january 15th 2025, and a vector of simulated TAMARS into the future. It returns the average TAMAR over that period '''
  if business_days_till_expiry < 1 or business_days_till_expiry > ((simulated_tamar).shape[0] - 1):
        raise ValueError("Problemas de matrix")

    # shape: (days_needed, M); row 0 is t0, so start at 1
  sim_tail = simulated_tamar[1:business_days_till_expiry+1, :]

  observed_matrix = np.tile(observed_TAMAR.reshape(-1, 1), (1, sim_tail.shape[1]))
  full_matrix = np.vstack([observed_matrix, sim_tail])

    # Per-path averages (vector length M); caller must not collapse with np.mean
  return np.mean(full_matrix, axis=0)

def convert_to_tamar_tem(average_tamar):
    '''this function is a helper that takes a TAMAR rate and converts it to a monthly percent return using the equation given by the Argentine Government'''
    return (((1 + average_tamar / (365/32)) ** (365/32)) ** (1/12))-1

def vpv(tamar_tem, accrual_days_360):
  '''usiing the equation for VPV given by the governmnet, this function takes a TAMAR_tem (as a monthly percent) and the accrual days (in days 360) and returns the VPV of the bond'''
  vpv = 100.0 * (1.0 + tamar_tem) ** ((accrual_days_360 /360)*12)
  return vpv

def get_vpv_vector_given_average_tamar_vector(average_tamar_vector,guaranteed_tamar_tem,accrual_days_360):
  '''given an aevrage tamar vector until 10 business days before expiry, a guaranteed tamar_tem rate, and accrual days 360, this returns a vector of VPVs with the floor'''
  variable_vpv_vector = np.zeros(M)
  for i in range(M):
    variable_vpv_vector[i] = vpv(tamar_tem = max(convert_to_tamar_tem(average_tamar_vector[i]),guaranteed_tamar_tem),accrual_days_360 = accrual_days_360)
  return variable_vpv_vector




def discounted_value(non_discount_value, fr_equiv, expiry_date, today = None):
  '''this is a helped method to discount any zero coupon asset to today.
  args: non discount value = value to be discounted
  fr_equiv = this is the equivalent fixed rate you can get over the same period
  expiry_date = this is the date of expiry of the zero coupon asset, should be in the form year-month-day
  today is none by default and if it is none it will run a local dt calc, otherwise you can specify todays date to be more precise
  returns: the discounted value of the instrument
  '''
  expiry_date = pd.to_datetime(expiry_date)
  if today == None:
    today = pd.Timestamp(date.today()) # Convert datetime.date to pandas.Timestamp
    days_360_till_expiry = get_distance_days_360(today, expiry_date) #uses days 360 helper method to ensure consistent discounting
  else:
    today = pd.to_datetime(today) #  convert day to datetime object if it was specified
  discounted_value = non_discount_value/(((1+fr_equiv)**12)**(days_360_till_expiry/360))    #non_discount_value /(( (1 + fr_equiv)**12) ** (days_365_till_expiry/365))
  return discounted_value

def get_terminal_value(expiry_date, guaranteed_tamar_tem, simulation_type):
  '''this function calls all the other helper functions and makes necessary print statements to make it clear what its calculating. It should be clear
  that this function returns non discounted values'''
  expiry_date = pd.to_datetime(expiry_date)
  accrual_days_360 = get_distance_days_360(emission_date, expiry_date) #accrual days is the days from emission to expiry
  print(f'total accrual days in days 360: {accrual_days_360}')
  days_left_252 = get_distance_days_252(most_recent_tamar_date, expiry_date)-10 # days left is the amount of business days left since the most recent TAMAR release until expiry - 10 (since stops 10 days business days before expiry)
  print(f'total days left to simulate in business days:{days_left_252}')
  print(f'total days already observed in business days:{len(observed_TAMAR)}')
  guaranteed_vpv = vpv(guaranteed_tamar_tem, accrual_days_360)
  print(f'guaranteed terminal value {guaranteed_vpv}')
  guaranteed_present_value = discounted_value(guaranteed_vpv,discount_rate,bond_expiry)

  print(f'guarrantee present value = {guaranteed_present_value}')
  guaranteed_vpv_vector = np.full(M, guaranteed_vpv)
  average_tamar_vector = average_tamar(observed_TAMAR, simulation_type, days_left_252)
  #average_tamar_df = pd.DataFrame(average_tamar_vector)
  #average_tamar_mean = average_tamar_df.mean()
  #print(convert_to_tamar_tem(average_tamar_mean))
  #print(f'Average TAMAR accross simulations till expiry {float(average_tamar_mean)}')
  variable_vpv_vector = get_vpv_vector_given_average_tamar_vector(average_tamar_vector, guaranteed_tamar_tem, accrual_days_360)
  discounted_variable_vpv_vector = discounted_value(variable_vpv_vector,discount_rate,bond_expiry)
  vpv_var = np.var(variable_vpv_vector)
  non_discount_option_value = np.mean(variable_vpv_vector-guaranteed_vpv_vector)
  print(f'first five examples of VPV after applying floor: {variable_vpv_vector[:5]}')
  variable_vpv_vector_df = pd.DataFrame(variable_vpv_vector)
  variable_vpv_std = variable_vpv_vector_df.std(ddof=1)
  mean_vpv_with_floor = np.mean(variable_vpv_vector)
  print(f'average VPV with floor (no discount){mean_vpv_with_floor}')
  print(f'non discounted option value: {non_discount_option_value}')
  return float(non_discount_option_value), float(mean_vpv_with_floor), guaranteed_vpv, vpv_var, discounted_variable_vpv_vector


def discounted_data(terminal_values_tuple, discount_rate, bond_expiry, trading_price,bond_name,figure_number):
  non_discount_option_value, vpv_with_floor, guaranteed_terminal_value, vpv_var, discounted_variable_vpv_vector = terminal_values_tuple

  discounted_option = discounted_value(non_discount_option_value,discount_rate,bond_expiry)
  print(f'value of discounted option = {discounted_option}')
  discounted_vpv = discounted_value(vpv_with_floor,discount_rate,bond_expiry)

  guaranteed_present_value = discounted_value(guaranteed_terminal_value,discount_rate,bond_expiry)
  market_implied_option_value = trading_price - guaranteed_present_value
  print(f'market implied option value = {market_implied_option_value}')


  difference_in_view = discounted_vpv - trading_price
  print(f'simulated discounted risk neutral fair value = {discounted_vpv}')
  print(f'trading price = {trading_price}')
  difference_in_option_price = discounted_option - market_implied_option_value
  print(f'difference in market price to house view = {difference_in_option_price}')
  print(f'variance in payment = {float((vpv_var))}')
  print(f'estimated risk aversion coefficient = {float((difference_in_view/(vpv_var)))}')
  discounted_variable_vpv_vector_df = pd.DataFrame(discounted_variable_vpv_vector, columns= [None])
  
  C1_color = (0 / 255, 121 / 255, 204 / 255)
  C2_color = (127 / 255, 127 / 255, 127 / 255)
  C3_color = (0 / 255, 49 / 255, 77 / 255)
  
  ax = discounted_variable_vpv_vector_df.hist(bins=35, color = C2_color)
  ax[0,0].set_ylabel('Frequency', fontsize = 10 )
  ax[0,0].set_xlabel('Discounted Terminal Values with floor (in Pesos)', fontsize = 10)
  ax[0,0].axvline(x=trading_price, color= C1_color, linestyle='--', label='Trading Price')
  # remove vertical gridlines, keep horizontal
  #ax.grid(visible = False ,which = "both" axis = 'x')

  # Calculate 95% confidence interval
  lower_bound = np.percentile(discounted_variable_vpv_vector, 2.5)
  upper_bound = np.percentile(discounted_variable_vpv_vector, 97.5)

  ax[0,0].axvline(x=lower_bound, color='black', linestyle=':', label='95% CI Lower Bound')
  ax[0,0].axvline(x=upper_bound, color='black', linestyle=':', label='95% CI Upper Bound')

  ax[0,0].legend()
  plt.title(f'Figure {figure_number}. Histogram of Discounted Terminal Values for {bond_name}', loc='left', fontweight='bold', fontsize=14, x=-0.08, pad=15)
  plt.show()
  return discounted_vpv, vpv_var**(1/2), non_discount_option_value, vpv_with_floor
